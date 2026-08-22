"""
Heavenly Tribulation Engine (*Tianjie*) — multi-wave lightning storms.

Interactive: the route resolves ONE WAVE per action call
(endure / sacrifice artifact / shield pill / bail).
Pure math only — persistence and DB side-effects live in routes.

Damage model (all tunables in core/balance.py → TRIBULATION):
  raw = D_base(target) × wave_mult(W) × (1 + escalation·b) × (target/4)^1.35
  → power-ratio mitigation (capped) → physique % (physical waves)
  → sacrifice full-absorb → shield pill → gear soak (physical only)
  → Qi pool absorbs → body pool; body empty = body destroyed.
Wave 4 is not damage — it is a willpower contest vs inner demons;
Dao Heart hitting zero means the soul itself burns.
"""
import json
import random
from typing import Dict, Any, Optional, Tuple, List

from core.balance import TRIBULATION, get_root_config


# ── Tier selection ───────────────────────────────────────────────────

def select_tier(spiritual_root: str, karma_sin: int) -> Tuple[str, int]:
    """Heaven judges talent and sin. Returns (tier_name, total_strikes)."""
    cfg = get_root_config(spiritual_root)
    if spiritual_root in TRIBULATION["nine_nine_roots"] or karma_sin >= TRIBULATION["nine_nine_karma"]:
        tier = "NINE_NINE"
    elif cfg["rarity"] in TRIBULATION["six_nine_root_rarities"] or karma_sin >= TRIBULATION["six_nine_karma"]:
        tier = "SIX_NINE"
    else:
        tier = "FOUR_NINE"
    return tier, TRIBULATION["tier_strikes"][tier]


def root_elements(spiritual_root: str) -> List[str]:
    return get_root_config(spiritual_root).get("elements", [])


# ── Power composite ──────────────────────────────────────────────────

def compute_t_score(
    realm: int,
    stage_index: int,
    equipped_artifact_powers: float,
    physique_tier: int,
    luck_stat: int
) -> float:
    w = TRIBULATION["t_score"]
    return round(
        realm * w["realm_weight"]
        + stage_index * w["stage_index_weight"]
        + equipped_artifact_powers / w["artifact_power_divisor"]
        + physique_tier * w["physique_tier_weight"]
        + luck_stat * w["luck_weight"],
        2,
    )


def _mitigation_ratio(t_score: float, target_realm: int) -> float:
    softener = TRIBULATION["defense_softener"]
    reference = max(1.0, TRIBULATION["base_strike_damage"].get(target_realm, 40) / 4.0 * softener / 10.0)
    ratio = TRIBULATION["defense_ratio_cap"] * (t_score / (t_score + reference))
    return min(TRIBULATION["defense_ratio_cap"], ratio)


def _strike_damage(state: Dict[str, Any], wave_no: int, strike_b: int) -> float:
    d_base = TRIBULATION["base_strike_damage"].get(state["target_realm"], 40)
    wave_mult = TRIBULATION["wave_multiplier"][wave_no]
    heaven_intensity = (state["target_realm"] / TRIBULATION["min_target_realm"]) ** TRIBULATION["t_score_exponent"]
    return d_base * wave_mult * (1.0 + TRIBULATION["strike_escalation"] * strike_b) * heaven_intensity


# ── Build ────────────────────────────────────────────────────────────

def build_tribulation(
    target_realm: int,
    spiritual_root: str,
    karma_sin: int,
    spirit_energy: float,
    max_energy: float,
    physique_tier: int,
    physique_resistance: float,
    luck_stat: int,
    dao_heart: float,
    equipped: Dict[str, Optional[Dict[str, Any]]],
    stage_index: int = 0
) -> Dict[str, Any]:
    """
    Snapshot everything needed for the storm into a JSON-safe dict.
    equipped: {"weapon": {...artifact def...} | None, "armor": ..., "banner": ...}
    """
    tier, total = select_tier(spiritual_root, karma_sin)

    gear = {}
    for slot in ("armor", "weapon", "banner"):
        art = equipped.get(slot)
        gear[slot] = (
            {"id": art["id"], "name": art["name"], "power_left": float(art.get("power", 0))}
            if art else None
        )

    waves = []
    allocated = 0
    for w_def in TRIBULATION["waves"]:
        strikes = int(round(total * w_def["strikes_ratio"]))
        waves.append({"wave": w_def["wave"], "type": w_def["type"], "strikes": strikes})
        allocated += strikes
    waves[-1]["strikes"] += total - allocated  # absorb rounding drift

    t_score = compute_t_score(
        realm=target_realm - 1,
        stage_index=stage_index,
        equipped_artifact_powers=sum(g["power_left"] for g in gear.values() if g),
        physique_tier=physique_tier,
        luck_stat=luck_stat,
    )

    return {
        "target_realm": target_realm,
        "tier": tier,
        "total_strikes": total,
        "_waves": waves,
        "wave_index": 0,
        "strikes_done_total": 0,
        "qi_pool": round(max(0.0, spirit_energy), 2),
        "body_pool": round(max_energy * TRIBULATION["body_pool_factor"], 2),
        "body_pool_max": round(max_energy * TRIBULATION["body_pool_factor"], 2),
        "_meridian_damage": 0.0,
        "shield": 0.0,
        "next_wave_absorb": False,
        "gear": gear,
        "physique_resistance": physique_resistance,
        "dao_heart": round(dao_heart, 2),
        "karma_sin": karma_sin,
        "luck_stat": luck_stat,
        "t_score": t_score,
        "destroyed_artifacts": [],
        "log": [
            f"☁️ The sky BLACKENS. A {total}-strike {tier.replace('_', '-')} Tribulation gathers "
            f"above your crossing into Realm {target_realm}!"
        ],
    }


# ── Resolution ───────────────────────────────────────────────────────

def resolve_wave(
    state: Dict[str, Any],
    action: str,
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """
    Resolves the ENTIRE next wave given the cultivator's choice.
    action: "endure" | "sacrifice:<slot>" | "pill" | "bail"
    Returns {"state": updated, "outcome": ONGOING|SURVIVED|DESTROYED|BAILED|INVALID, "events": [...]}
    """
    rng = rng or random
    events: List[str] = []

    if action == "bail":
        state["log"].append("🏳️ You flee the storm. Heaven remembers cowardice.")
        return {"state": state, "outcome": "BAILED", "events": ["You turned your back on heaven's judgment."]}

    # Sacrifice: destroy an equipped artifact to nullify this whole wave
    if action.startswith("sacrifice"):
        slot = action.split(":", 1)[1] if ":" in action else "weapon"
        art = state["gear"].get(slot)
        if not art:
            return {"state": state, "outcome": "INVALID",
                    "events": [f"No equipped artifact in slot '{slot}' to sacrifice."]}
        events.append(
            f"🗡️ You HURL your {art['name']} into the clouds! It detonates in a blaze of "
            f"spirit-light, devouring the entire incoming wave!"
        )
        state["log"].append(events[-1])
        state["next_wave_absorb"] = True
        state["gear"][slot] = None

    if state["wave_index"] >= len(state["_waves"]):
        return {"state": state, "outcome": "SURVIVED", "events": ["The storm has already passed."]}

    plan = state["_waves"][state["wave_index"]]
    wave_no = plan["wave"]

    if plan["type"] == "HEART_DEMON":
        outcome_events = _resolve_heart_demon(state, plan, rng)
        events.extend(outcome_events)
    else:
        outcome_events = _resolve_strikes(state, plan, rng)
        events.extend(outcome_events)

    state["log"].extend(events)

    if state.get("_dead"):
        return {"state": state, "outcome": "DESTROYED", "events": events}
    if state["wave_index"] >= len(state["_waves"]):
        events.append(
            f"🌅 THE STORM PARTS. Heaven acknowledges your crossing! "
            f"({state['strikes_done_total']}/{state['total_strikes']} strikes endured)"
        )
        state["log"].append(events[-1])
        return {"state": state, "outcome": "SURVIVED", "events": events}
    return {"state": state, "outcome": "ONGOING", "events": events}


def _resolve_strikes(state: Dict[str, Any], plan: Dict[str, Any], rng: random.Random) -> List[str]:
    events: List[str] = []
    wave_no = plan["wave"]
    wtype = plan["type"]
    strikes = plan["strikes"]

    for b in range(1, strikes + 1):
        raw = _strike_damage(state, wave_no, b)

        mitig = _mitigation_ratio(state["t_score"], state["target_realm"])
        dmg = raw * (1.0 - mitig)

        if wtype == "PHYSICAL":
            dmg *= 1.0 - min(0.9, state["physique_resistance"] * TRIBULATION["physique_resistance_scale"])
        elif wtype == "SPIRITUAL":
            dmg *= 1.0 - min(0.45, state["physique_resistance"] * TRIBULATION["physique_resistance_scale"] * 0.5)

        if state["next_wave_absorb"]:
            dmg = 0.0
            if b == 1:
                events.append(f"✨ Wave {wave_no}: your sacrifice holds — lightning breaks around you harmlessly!")

        if state["shield"] > 0 and dmg > 0:
            absorbed = min(state["shield"], dmg)
            state["shield"] -= absorbed
            dmg -= absorbed
            if b == 1 and absorbed > 0:
                events.append(f"🛡️ Your ward flares, drinking {absorbed:.0f} damage of heavenly wrath.")

        if dmg > 0 and wtype == "PHYSICAL":
            for slot in ("armor", "weapon"):
                g = state["gear"].get(slot)
                if g and dmg > 0:
                    soak = min(g["power_left"], dmg)
                    g["power_left"] -= soak
                    dmg -= soak
                    if g["power_left"] <= 0:
                        state["destroyed_artifacts"].append(g["name"])
                        events.append(f"💥 Your {g['name']} SHATTERS under the storm!")
                        state["gear"][slot] = None

        if dmg > 0:
            qi_take = min(state["qi_pool"], dmg)
            state["qi_pool"] -= qi_take
            dmg -= qi_take
        if dmg > 0:
            body_take = min(state["body_pool"], dmg)
            state["body_pool"] -= body_take
            scar = body_take * TRIBULATION["meridian_scar_per_body_point"]
            state["_meridian_damage"] = min(
                TRIBULATION["death_meridian_threshold"],
                state["_meridian_damage"] + scar
            )
            if b == 1 or b == strikes:
                events.append(f"⚡ Strike {b}/{strikes} of wave {wave_no} tears through your guard — flesh scorched!")

        state["strikes_done_total"] += 1

        if state["body_pool"] <= 0 or state["_meridian_damage"] >= TRIBULATION["death_meridian_threshold"]:
            state["_dead"] = True
            events.append("🌋 Your body BURNS APART under heaven's wrath...")
            break

    state["next_wave_absorb"] = False
    state["wave_index"] += 1
    return events


def _resolve_heart_demon(state: Dict[str, Any], plan: Dict[str, Any], rng: random.Random) -> List[str]:
    events: List[str] = []
    bursts = TRIBULATION["heart_demon_bursts"]
    events.append("🔥 FINAL WAVE: the lightning parts... and your own heart walks out to meet you.")

    illusion = (
        TRIBULATION["illusion_power_base"]
        + TRIBULATION["illusion_power_per_target_realm"] * max(0, state["target_realm"] - TRIBULATION["min_target_realm"])
        + TRIBULATION["illusion_power_per_100_sin"] * (state["karma_sin"] / 100.0)
    )

    for burst in range(1, bursts + 1):
        attack = illusion * rng.uniform(0.85, 1.2)
        defense = (
            state["dao_heart"] * TRIBULATION["willpower_from_dao_heart"]
            + state["luck_stat"] * TRIBULATION["willpower_luck_weight"]
        ) * rng.uniform(0.85, 1.2)
        if defense >= attack:
            events.append(f"🧠 Illusion {burst}/{bursts}: you walk through your demons untouched.")
        else:
            state["dao_heart"] -= TRIBULATION["dao_heart_loss_per_burst_fail"]
            events.append(
                f"😱 Illusion {burst}/{bursts}: your deepest regret wears a familiar face. "
                f"Dao Heart -{TRIBULATION['dao_heart_loss_per_burst_fail']:.0f}!"
            )
        if state["dao_heart"] <= 0:
            state["dao_heart"] = 0.0
            state["_dead"] = True
            events.append("🖤 Your heart surrenders to the demon. Qi explodes inward — consumed from within.")
            break

    state["strikes_done_total"] += plan["strikes"]
    state["wave_index"] += 1
    return events


# ── Serialization & helpers ──────────────────────────────────────────

def serialize_state(state: Dict[str, Any]) -> str:
    return json.dumps(state, ensure_ascii=False)


def deserialize_state(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def near_miss_death(state: Dict[str, Any]) -> bool:
    """Died with the storm almost over? Maximum tragedy messaging."""
    return state["strikes_done_total"] >= state["total_strikes"] - max(3, int(state["total_strikes"] * 0.08))


def tribulation_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "target_realm": state["target_realm"],
        "tier": state["tier"],
        "total_strikes": state["total_strikes"],
        "strikes_endured": state["strikes_done_total"],
        "waves_remaining": max(0, len(state["_waves"]) - state["wave_index"]),
        "qi_pool": round(state["qi_pool"], 1),
        "body_pool": round(state["body_pool"], 1),
        "shield": round(state["shield"], 1),
        "dao_heart": round(state["dao_heart"], 1),
        "meridian_damage": round(state.get("_meridian_damage", 0.0), 3),
        "gear": {k: (v["name"] if v else None) for k, v in state["gear"].items()},
    }
