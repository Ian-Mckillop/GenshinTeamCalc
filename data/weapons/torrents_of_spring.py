import engine.entities as entities
import engine.models as models


def build_torrents_of_spring(refinement: int = 1) -> entities.Weapon:
    """
    Builds Torrents of Spring (5-star Claymore, Lv. 90, 741 Base ATK, 16.5% ATK).
    Passive — Wavebreaking Thunder (R1–R5):
    - Unconditional +16% / 20% / 24% / 28% / 32% ATK to the equipping character.
    - Electro hits grant "Attendant's Measure" for 15s (+20% / 25% / 30% / 35% / 40%
      Stellar-Conduct Reaction DMG% for the active character).
    - While active, hits from the equipping character considered Stellar-Conduct DMG
      enhance the effect (+16%..32% extra ATK to wearer & +20%..40% extra Stellar-Conduct
      Reaction DMG% to the active character). Works off-field.
    """
    r_idx = max(1, min(5, refinement)) - 1
    atk_bonus = 0.16 + 0.04 * r_idx
    sc_dmg_bonus = 0.20 + 0.05 * r_idx

    state_rules = [
        # Electro hit by wearer grants/refreshes "Attendant's Measure" for 15.0s (works off-field)
        models.StateRule(
            state_id="Attendant's Measure",
            base_duration=15.0,
            trigger_tags=["HIT", "Electro"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
        # While "Attendant's Measure" is active, wearer's Stellar-Conduct hits enhance the effect
        models.StateRule(
            state_id="Attendant's Measure Enhanced",
            base_duration=float("inf"),
            trigger_tags=["HIT", "Stellar-Conduct"],
            trigger_scope="SELF",
            required_states=["Attendant's Measure"],
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
        # Clear enhanced state when "Attendant's Measure" expires
        models.StateRule(
            state_id="Attendant's Measure Expire Cleanup",
            base_duration=0.0,
            trigger_tags=["STATE_EXPIRE", "Attendant's Measure"],
            termination_rules=["Attendant's Measure Enhanced"],
            target_scope="GLOBAL",
        ),
    ]

    buff_rules = [
        # Secondary Stat: 16.5% ATK
        models.BuffRule(
            buff_id="TORRENTS_OF_SPRING_SUBSTAT_ATK",
            buff_name="Torrents of Spring Substat ATK%",
            stat="ATK%",
            base_value=0.165,
            target_scope="SELF",
        ),
        # Passive Base: +16%..32% ATK to equipping character
        models.BuffRule(
            buff_id="TORRENTS_OF_SPRING_BASE_ATK",
            buff_name="Wavebreaking Thunder ATK%",
            stat="ATK%",
            base_value=atk_bonus,
            target_scope="SELF",
        ),
        # Attendant's Measure: +20%..40% Stellar-Conduct Reaction DMG% for active character
        models.BuffRule(
            buff_id="TORRENTS_OF_SPRING_ACTIVE_SC_DMG",
            buff_name="Attendant's Measure Active Stellar-Conduct DMG%",
            stat="Reaction DMG%",
            base_value=sc_dmg_bonus,
            required_states=["Attendant's Measure"],
            target_scope="ON_FIELD",
            ability_filters=["Stellar-Conduct"],
        ),
        # Enhanced Attendant's Measure: +16%..32% extra ATK to equipping character
        models.BuffRule(
            buff_id="TORRENTS_OF_SPRING_ENHANCED_ATK",
            buff_name="Wavebreaking Thunder Enhanced ATK%",
            stat="ATK%",
            base_value=atk_bonus,
            required_states=["Attendant's Measure", "Attendant's Measure Enhanced"],
            target_scope="SELF",
        ),
        # Enhanced Attendant's Measure: +20%..40% extra Stellar-Conduct Reaction DMG% for active character
        models.BuffRule(
            buff_id="TORRENTS_OF_SPRING_ENHANCED_SC_DMG",
            buff_name="Attendant's Measure Enhanced Active Stellar-Conduct DMG%",
            stat="Reaction DMG%",
            base_value=sc_dmg_bonus,
            required_states=["Attendant's Measure", "Attendant's Measure Enhanced"],
            target_scope="ON_FIELD",
            ability_filters=["Stellar-Conduct"],
        ),
    ]

    return entities.Weapon(
        name="Torrents of Spring",
        type="Claymore",
        base_atk=741.0,
        state_rules=state_rules,
        buff_rules=buff_rules,
    )