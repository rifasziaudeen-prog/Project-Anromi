from sqlalchemy import Column, Integer, String, Float, JSON
from core.database import Base


class WorldNode(Base):
    """
    Open-world graph node. Seeded idempotently from core/balance.WORLD_NODES
    at startup — edit balance.py, restart, and the world updates itself.
    """
    __tablename__ = "world_nodes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    plane = Column(String, default="Mortal Domain")
    spirit_density = Column(Float, default=1.0)          # meditation multiplier
    elemental_bias = Column(String, default="Balanced")  # boosts matching roots
    danger_tier = Column(Integer, default=1)             # 1-16 risk level
    connected_node_ids = Column(JSON, default=list)      # adjacency
    description = Column(String, default="")
