import engine.entities as entities
import engine.models as models


def build_epochal_advent() -> entities.ArtifactSet:
    state_rules = [
        models.StateRule(
            state_id="Starspark",
            base_duration=3.0,
            trigger_tags=["CAST", "Elemental Skill"],
            max_stacks=2,
            refresh_mode="SEQUENTIAL",
            pause_off_field=True,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Starspark",
            base_duration=3.0,
            trigger_tags=["CAST", "Elemental Burst"],
            max_stacks=2,
            refresh_mode="SEQUENTIAL",
            pause_off_field=True,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Starspark",
            base_duration=3.0,
            trigger_tags=["CAST", "Normal Attack"],
            max_stacks=2,
            refresh_mode="SEQUENTIAL",
            pause_off_field=True,
            target_scope="SELF",
        ),
    ]

    buff_rules = [
        models.BuffRule(
            buff_id="EPOCHAL_ADVENT_CRYO_CR",
            buff_name="Undying Radiance Cryo CRIT Rate",
            stat="Crit Rate",
            base_value=0.20,
            required_states=["Starspark"],
            target_scope="SELF",
            element_filters=["Cryo"],
        ),
        models.BuffRule(
            buff_id="EPOCHAL_ADVENT_STELLAR_CR",
            buff_name="Undying Radiance Stellar Glimmer CRIT Rate",
            stat="Crit Rate",
            base_value=0.20,
            required_states=["Starspark"],
            target_scope="SELF",
            element_filters=["Cryo"],
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    return entities.ArtifactSet(
        name="Epochal Advent",
        two_piece_stats={"ATK%": 0.18},
        state_rules=state_rules,
        buff_rules=buff_rules,
    )