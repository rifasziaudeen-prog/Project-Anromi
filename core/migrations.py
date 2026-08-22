"""
Generic startup auto-migration for SQLite prototyping.
`Base.metadata.create_all` creates MISSING tables but never alters existing
ones — this module diffs every model against the live database and adds any
missing columns automatically. You never need to hand-write migrations while
prototyping: edit models, restart, done. Delete anromi.db anytime for a fresh start.
"""
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from core.database import Base


def _import_all_models() -> None:
    """
    Imports every module in the models package so all ORM tables register
    with Base.metadata. Auto-discovers new model files — no manual imports needed.
    """
    import importlib
    import pkgutil
    import models

    for m in pkgutil.iter_modules(models.__path__):
        importlib.import_module(f"models.{m.name}")


def _render_default(col) -> str:
    """Renders a SQL literal for a column's scalar default (for NOT NULL adds)."""
    d = col.default
    if d is not None and getattr(d, "is_scalar", False):
        val = d.arg
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return repr(val)
        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"
    return "NULL"


async def run_startup_migrations(engine: AsyncEngine) -> None:
    _import_all_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def _patch(sync_conn):
            inspector = inspect(sync_conn)
            existing_tables = set(inspector.get_table_names())
            for table in Base.metadata.sorted_tables:
                if table.name not in existing_tables:
                    continue
                existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
                for col in table.columns:
                    if col.name not in existing_cols:
                        col_type = col.type.compile(sync_conn.dialect)
                        ddl = f'"{col.name}" {col_type}'
                        if not col.nullable:
                            ddl += f" DEFAULT {_render_default(col)} NOT NULL"
                        sync_conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN {ddl}'))
                    # Backfill any NULL rows so Python-side defaults always hold
                    if col.default is not None and getattr(col.default, "is_scalar", False):
                        sync_conn.execute(text(
                            f'UPDATE "{table.name}" SET "{col.name}" = {_render_default(col)} '
                            f'WHERE "{col.name}" IS NULL'
                        ))

            _seed_world_nodes(sync_conn, existing_tables)

        await conn.run_sync(_patch)


def _seed_world_nodes(sync_conn, existing_tables) -> None:
    """Upserts the balance-defined world graph into world_nodes (idempotent)."""
    import json
    from core.balance import WORLD_NODES, WORLD

    if "world_nodes" not in existing_tables:
        return
    for node_id, node in WORLD_NODES.items():
        # Ensure adjacency is symmetric so travel always works both ways
        connections = sorted(set(node["connections"]))
        sync_conn.execute(text(
            'INSERT INTO world_nodes (id, name, region, plane, spirit_density, elemental_bias, danger_tier, connected_node_ids, description) '
            'VALUES (:id, :name, :region, :plane, :density, :bias, :danger, :conn, :desc) '
            'ON CONFLICT(id) DO UPDATE SET name=:name, region=:region, plane=:plane, spirit_density=:density, '
            'elemental_bias=:bias, danger_tier=:danger, connected_node_ids=:conn, description=:desc'
        ), {
            "id": node_id,
            "name": node["name"],
            "region": node["region"],
            "plane": node.get("plane", "Mortal Domain"),
            "density": node.get("spirit_density", 1.0),
            "bias": node.get("elemental_bias", "Balanced"),
            "danger": node.get("danger_tier", 1),
            "conn": json.dumps(connections),
            "desc": node.get("description", ""),
        })
    # Guarantee every user stands somewhere valid
    start = WORLD["starting_node"]
    if start in WORLD_NODES:
        sync_conn.execute(text(
            'UPDATE users SET current_node_id = :start '
            "WHERE current_node_id IS NULL OR current_node_id NOT IN (SELECT id FROM world_nodes)"
        ), {"start": start})
