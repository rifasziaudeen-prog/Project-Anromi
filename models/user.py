from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum as SQLEnum
from datetime import datetime, timezone
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    dao_title = Column(String, default="Wandering Cultivator")

    # 16-Realm Cultivation Progression
    realm = Column(Integer, default=1) # 1 = Qi Condensation ... 9 = True Immortal ... 16 = Eternal Transcendent
    stage = Column(String, default="Layer 1") # "Layer 1"-"Layer 9", "Great Circle", or "Early Stage"-"Peak Stage"
    
    # Meridian & Spiritual Qi State
    spirit_energy = Column(Float, default=10.0)      # Current Q_curr
    max_energy = Column(Float, default=100.0)        # Meridian capacity Q_max
    qi_purity = Column(Float, default=0.75)          # Purity ratio [0.1, 1.0]
    meridian_damage = Column(Float, default=0.0)     # Meridian rupture debuff [0.0, 1.0]

    # Longevity & Time
    lifespan_current_years = Column(Float, default=16.0) # Age in simulated years
    lifespan_max_years = Column(Float, default=120.0)    # Natural longevity ceiling

    # Bottleneck & Comprehension
    is_bottleneck = Column(Boolean, default=False)
    bottleneck_comprehension = Column(Float, default=0.0) # Accumulated breakthrough insight

    # Talent, Roots & Physique
    spiritual_root = Column(String, default="Mortal Five-Element") # e.g. Mortal Five-Element, True Three-Element, Heaven Fire, Mutant Lightning
    spiritual_root_purity = Column(Float, default=0.50)
    physique_tier = Column(Integer, default=0) # 0 = Mortal Flesh, 1 = Iron Bone, 2 = Spirit Body, 3 = Ancient Sacred Body
    physique_name = Column(String, default="Mortal Flesh")

    # Dao Heart & Karma Meters
    dao_heart_stability = Column(Float, default=100.0) # [0, 100], drops on trauma/failure
    karma_sin = Column(Integer, default=0)             # Demonic Sin counter [0, 1000]

    # Hardcore Permadeath & Remnant Soul State
    is_dead = Column(Boolean, default=False)
    is_remnant_soul = Column(Boolean, default=False)
    remnant_soul_vitality = Column(Float, default=100.0) # Decays when in Remnant Soul state
    remnant_soul_since = Column(DateTime, nullable=True)  # When the soul left its body
    soul_state = Column(String, default="ALIVE")          # ALIVE / REMNANT_SOUL / DEAD
    death_count = Column(Integer, default=0)
    lineage_generation = Column(Integer, default=1)       # Reincarnation counter
    karmic_legacy_tokens = Column(Integer, default=0)    # Points inherited on reincarnation

    # Engagement & Psychology (streaks, variable rewards, sunk-cost tracking)
    streak_days = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_action_date = Column(String, nullable=True)      # "YYYY-MM-DD" UTC calendar day
    total_meditations = Column(Integer, default=0)
    total_breakthrough_wins = Column(Integer, default=0)
    total_breakthrough_fails = Column(Integer, default=0)
    dao_insight = Column(Integer, default=0)              # Windfall currency (jackpot reward)
    highest_realm_achieved = Column(Integer, default=1)

    # Dan Dao / Qi Dao crafting mastery & alchemy state
    luck_stat = Column(Integer, default=5)                 # Feeds windfalls, gathering, craft coincidences
    pill_toxicity = Column(Float, default=0.0)             # Dan Du [0, 100] — stalls Qi, hurts breakthroughs
    stored_breakthrough_bonus = Column(Float, default=0.0) # Booster pills waiting for the next attempt
    alchemy_exp = Column(Integer, default=0)
    alchemy_level = Column(Integer, default=1)
    forging_exp = Column(Integer, default=0)
    forging_level = Column(Integer, default=1)

    # Equipped artifacts (item ids from balance.ARTIFACTS; NULL = empty slot)
    equipped_weapon = Column(String, nullable=True)
    equipped_armor = Column(String, nullable=True)
    equipped_talisman = Column(String, nullable=True)
    equipped_banner = Column(String, nullable=True)

    # Gathering cooldown (placeholder until v0.4 world engine)
    last_gathered = Column(DateTime, nullable=True)

    # Open-world state (v0.4)
    current_node_id = Column(String, default="sect_valley")
    travel_locked_until = Column(DateTime, nullable=True)   # mid-journey lockout

    # Active Heavenly Tribulation — JSON snapshot persisted between wave actions
    active_tribulation = Column(String, nullable=True)

    # Economy & Wealth (low-grade stones; higher grades live in inventory)
    spirit_stones = Column(Integer, default=10)

    # Metadata & Timestamps
    last_meditated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
