import engine.entities as entities
import engine.models as models


def build_echoes_of_the_heart(refinement: int = 1) -> entities.Weapon:
    """
    Builds Echoes of the Heart (4-star Catalyst, Lv. 90, 565 Base ATK, 27.6% ATK).
    Passive — Echo of a Vow (R1–R5):
    - Triggering an Elemental Reaction increases the equipping character's
      Elemental Mastery by 60 / 75 / 90 / 105 / 120 for 12s.
    - Triggering a Stellar Glimmer reaction increases their Stellar Glimmer
      reaction DMG dealt by 16% / 20% / 24% / 28% / 32% for 12s.
    - Both effects can trigger even when the equipping character is off-field.
    """
    r_idx = max(1, min(5, refinement)) - 1
    em_bonus = 60.0 + 15.0 * r_idx
    sg_dmg_bonus = 0.16 + 0.04 * r_idx

    state_rules = [
        # Any Elemental Reaction triggered by wearer grants +60..120 EM for 12.0s (works off-field)
        models.StateRule(
            state_id="Echo of a Vow: EM",
            base_duration=12.0,
            trigger_tags=["REACTION"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        # Triggering a Stellar Glimmer reaction grants +16%..32% Stellar Glimmer Reaction DMG% for 12.0s
        models.StateRule(
            state_id="Echo of a Vow: SG DMG",
            base_duration=12.0,
            trigger_tags=["REACTION", "Stellar Glimmer"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
    ]

    buff_rules = [
        # Passive Part 1: +60..120 EM for 12s after triggering an Elemental Reaction
        models.BuffRule(
            buff_id="ECHOES_OF_THE_HEART_EM",
            buff_name="Echo of a Vow Elemental Mastery",
            stat="Elemental Mastery",
            base_value=em_bonus,
            required_states=["Echo of a Vow: EM"],
            target_scope="SELF",
        ),
        # Passive Part 2: +16%..32% Stellar Glimmer Reaction DMG% for 12s
        models.BuffRule(
            buff_id="ECHOES_OF_THE_HEART_SG_DMG",
            buff_name="Echo of a Vow Stellar Glimmer Reaction DMG%",
            stat="Reaction DMG%",
            base_value=sg_dmg_bonus,
            required_states=["Echo of a Vow: SG DMG"],
            target_scope="SELF",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    return entities.Weapon(
        name="Echoes of the Heart",
        type="Catalyst",
        base_atk=565.0,
        secondary_stats={"ATK%": 0.276},
        state_rules=state_rules,
        buff_rules=buff_rules,
    )