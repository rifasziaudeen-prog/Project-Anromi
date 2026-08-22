from enum import IntEnum, Enum
from typing import List, Dict, Any

class RealmTier(IntEnum):
    # Mortal / Human & Earth Step (Realms 1 - 8: 9 Layers + Great Circle)
    QI_CONDENSATION = 1          # 炼气期
    FOUNDATION_ESTABLISHMENT = 2 # 筑基期
    GOLDEN_CORE = 3              # 金丹期
    NASCENT_SOUL = 4             # 元婴期 (★ Remnant Soul survival unlocks)
    DEITY_TRANSFORMATION = 5     # 化神期
    VOID_REFINEMENT = 6          # 炼虚期
    BODY_INTEGRATION = 7         # 合体期
    MAHAYANA = 8                 # 大乘期 / 渡劫期

    # Heaven & Immortal Step (Realms 9 - 15: Early, Middle, Late, Peak)
    TRUE_IMMORTAL = 9            # 真仙境
    GOLDEN_IMMORTAL = 10         # 金仙境
    TAIYI_GOLDEN_IMMORTAL = 11   # 太乙金仙境
    DALUO_GOLDEN_IMMORTAL = 12   # 大罗金仙境
    QUASI_SAINT = 13             # 准圣 / 道祖境
    CHAOS_SAINT = 14             # 混元圣人境
    SOVEREIGN = 15               # 道境 / 创世神境

    # Cosmic / Supreme Step (Realm 16)
    ETERNAL_TRANSCENDENT = 16    # 超脱境 / 不朽境


class SubstageType(str, Enum):
    NINE_LAYERS = "nine_layers"       # Layer 1 - 9 + Great Circle
    FOUR_STAGES = "four_stages"       # Early, Middle, Late, Peak
    SUPREME = "supreme"               # Absolute Perfection


NINE_LAYERS_STAGES: List[str] = [
    "Layer 1", "Layer 2", "Layer 3",
    "Layer 4", "Layer 5", "Layer 6",
    "Layer 7", "Layer 8", "Layer 9",
    "Great Circle"
]

FOUR_STAGES_LIST: List[str] = [
    "Early Stage", "Middle Stage", "Late Stage", "Peak Stage"
]

SUPREME_STAGES_LIST: List[str] = [
    "Absolute Perfection"
]


REALM_METADATA: Dict[int, Dict[str, Any]] = {
    1: {
        "name_en": "Qi Condensation",
        "name_cn": "炼气期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 120,
        "base_max_qi": 100.0,
        "qi_multiplier_per_stage": 1.25,
        "base_absorption_rate": 1.0,
        "remnant_soul_capable": False,
        "description": "Opening meridians, drawing ambient spiritual Qi into the Dantian."
    },
    2: {
        "name_en": "Foundation Establishment",
        "name_cn": "筑基期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 250,
        "base_max_qi": 1000.0,
        "qi_multiplier_per_stage": 1.30,
        "base_absorption_rate": 2.5,
        "remnant_soul_capable": False,
        "description": "Condensing gaseous Qi into liquid spiritual essence, casting the Dao Foundation."
    },
    3: {
        "name_en": "Golden Core",
        "name_cn": "金丹期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 500,
        "base_max_qi": 8000.0,
        "qi_multiplier_per_stage": 1.35,
        "base_absorption_rate": 6.0,
        "remnant_soul_capable": False,
        "description": "Crystallizing liquid spiritual pool into an indestructible Golden Core of Grade 1-9."
    },
    4: {
        "name_en": "Nascent Soul",
        "name_cn": "元婴期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 1200,
        "base_max_qi": 50000.0,
        "qi_multiplier_per_stage": 1.40,
        "base_absorption_rate": 15.0,
        "remnant_soul_capable": True,
        "description": "Shattering the Core to birth the Nascent Soul. Soul projection and Remnant Soul survival unlocked."
    },
    5: {
        "name_en": "Deity Transformation",
        "name_cn": "化神期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 3000,
        "base_max_qi": 250000.0,
        "qi_multiplier_per_stage": 1.45,
        "base_absorption_rate": 35.0,
        "remnant_soul_capable": True,
        "description": "Transforming the soul into divine spirit sense, awakening primordial domain of intent."
    },
    6: {
        "name_en": "Void Refinement",
        "name_cn": "炼虚期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 8000,
        "base_max_qi": 1200000.0,
        "qi_multiplier_per_stage": 1.50,
        "base_absorption_rate": 80.0,
        "remnant_soul_capable": True,
        "description": "Melding soul and void, severing mortal ties and perceiving spatial laws."
    },
    7: {
        "name_en": "Body Integration",
        "name_cn": "合体期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 20000,
        "base_max_qi": 6000000.0,
        "qi_multiplier_per_stage": 1.55,
        "base_absorption_rate": 200.0,
        "remnant_soul_capable": True,
        "description": "Unifying physical vessel, Nascent Soul, and worldly laws into singular harmony."
    },
    8: {
        "name_en": "Mahayana",
        "name_cn": "大乘期",
        "substage_type": SubstageType.NINE_LAYERS,
        "stages": NINE_LAYERS_STAGES,
        "base_lifespan_years": 50000,
        "base_max_qi": 30000000.0,
        "qi_multiplier_per_stage": 1.60,
        "base_absorption_rate": 500.0,
        "remnant_soul_capable": True,
        "description": "Great vehicle perfection, standing at the summit of mortal realms awaiting Immortal Calamity."
    },
    9: {
        "name_en": "True Immortal",
        "name_cn": "真仙境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 200000,
        "base_max_qi": 200000000.0,
        "qi_multiplier_per_stage": 2.0,
        "base_absorption_rate": 2000.0,
        "remnant_soul_capable": True,
        "description": "Transmuting mortal essence into Immortal Qi, condensing the True Dao Fruit."
    },
    10: {
        "name_en": "Golden Immortal",
        "name_cn": "金仙境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 1000000,
        "base_max_qi": 1000000000.0,
        "qi_multiplier_per_stage": 2.2,
        "base_absorption_rate": 8000.0,
        "remnant_soul_capable": True,
        "description": "Forging an indestructible Golden Immortal body, unmarred by thousands of earthly tribulations."
    },
    11: {
        "name_en": "Taiyi Golden Immortal",
        "name_cn": "太乙金仙境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 10000000,
        "base_max_qi": 8000000000.0,
        "qi_multiplier_per_stage": 2.5,
        "base_absorption_rate": 30000.0,
        "remnant_soul_capable": True,
        "description": "Comprehending profound laws of the three realms, mastering elemental genesis."
    },
    12: {
        "name_en": "Daluo Golden Immortal",
        "name_cn": "大罗金仙境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 100000000,
        "base_max_qi": 50000000000.0,
        "qi_multiplier_per_stage": 3.0,
        "base_absorption_rate": 120000.0,
        "remnant_soul_capable": True,
        "description": "Transcending the river of time and karmic fate; past, present, and future unified."
    },
    13: {
        "name_en": "Quasi-Saint",
        "name_cn": "准圣境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 1000000000,
        "base_max_qi": 300000000000.0,
        "qi_multiplier_per_stage": 3.5,
        "base_absorption_rate": 500000.0,
        "remnant_soul_capable": True,
        "description": "Severing the Three Corpses (Good, Evil, Self), standing half-a-step into Cosmic Sanctity."
    },
    14: {
        "name_en": "Chaos Saint",
        "name_cn": "混元圣人境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 999999999999,
        "base_max_qi": 2000000000000.0,
        "qi_multiplier_per_stage": 4.0,
        "base_absorption_rate": 2500000.0,
        "remnant_soul_capable": True,
        "description": "Living as long as the cosmos, unextinguishable throughout infinite world destructions."
    },
    15: {
        "name_en": "Sovereign",
        "name_cn": "道境 / 创世神境",
        "substage_type": SubstageType.FOUR_STAGES,
        "stages": FOUR_STAGES_LIST,
        "base_lifespan_years": 999999999999999,
        "base_max_qi": 10000000000000.0,
        "qi_multiplier_per_stage": 5.0,
        "base_absorption_rate": 10000000.0,
        "remnant_soul_capable": True,
        "description": "Breathing life into new multiverses, commanding supreme Primordial Dao."
    },
    16: {
        "name_en": "Eternal Transcendent",
        "name_cn": "超脱境",
        "substage_type": SubstageType.SUPREME,
        "stages": SUPREME_STAGES_LIST,
        "base_lifespan_years": -1, # Infinite
        "base_max_qi": 999999999999999.0,
        "qi_multiplier_per_stage": 1.0,
        "base_absorption_rate": 99999999.0,
        "remnant_soul_capable": True,
        "description": "Transcending the Heavenly Dao, the Great Void, and all concepts of existence and non-existence."
    }
}

def get_realm_meta(realm_tier: int) -> Dict[str, Any]:
    return REALM_METADATA.get(realm_tier, REALM_METADATA[1])

def get_stages_for_realm(realm_tier: int) -> List[str]:
    return get_realm_meta(realm_tier)["stages"]

def is_bottleneck_stage(realm_tier: int, stage_str: str) -> bool:
    """
    Identifies if the current stage is a critical bottleneck stage:
    - In 9-layer realms (1-8): Layer 3, Layer 6, Layer 9, and Great Circle are bottlenecks.
    - In 4-stage realms (9-15): Every stage transition (Early->Mid, Mid->Late, Late->Peak, Peak->Next) is a bottleneck.
    """
    if realm_tier >= 16:
        return False
    if realm_tier < 9: # Realms 1 to 8 (9 Layers)
        return stage_str in ["Layer 3", "Layer 6", "Layer 9", "Great Circle"]
    else: # Realms 9 to 15 (4 Stages)
        return stage_str in FOUR_STAGES_LIST
