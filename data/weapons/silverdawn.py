import engine.entities as entities
import engine.models as models


def build_silverdawn(refinement: int = 1) -> entities.Weapon:
    bonus = 0.40 + 0.10 * (refinement - 1)

    state_rules = [
        models.StateRule(
            state_id="White Crown's Bequest",
            base_duration=6.0,
            trigger_tags=["CAST", "Elemental Skill"],
            termination_rules=["White Crown Ext"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="White Crown's Bequest",
            base_duration=6.0,
            trigger_tags=["CAST", "Elemental Burst"],
            termination_rules=["White Crown Ext"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="White Crown Ext",
            base_duration=30.0,
            trigger_tags=["HIT", "Stellar"],
            required_states=["White Crown's Bequest"],
            freeze_state=["White Crown's Bequest"],
            extend_duration=3.0,
            max_stacks=8,
            refresh_mode="INDEPENDENT",
            trigger_icd=0.1,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="White Crown Ext",
            base_duration=30.0,
            trigger_tags=["REACTION", "Stellar"],
            required_states=["White Crown's Bequest"],
            freeze_state=["White Crown's Bequest"],
            extend_duration=3.0,
            max_stacks=8,
            refresh_mode="INDEPENDENT",
            trigger_icd=0.1,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="White Crown Ext Cleanup",
            base_duration=0.0,
            trigger_tags=["STATE_EXPIRE", "White Crown's Bequest"],
            termination_rules=["White Crown Ext"],
            target_scope="SELF",
        ),
    ]

    buff_rules = [
        models.BuffRule(
            buff_id="SILVERDAWN_ATK",
            buff_name="White Crown's Bequest ATK%",
            stat="ATK%",
            base_value=bonus,
            required_states=["White Crown's Bequest"],
            target_scope="SELF",
        ),
        models.BuffRule(
            buff_id="SILVERDAWN_STELLAR_CD",
            buff_name="White Crown's Bequest Stellar Glimmer Crit DMG",
            stat="Crit Damage",
            base_value=bonus,
            required_states=["White Crown's Bequest"],
            target_scope="SELF",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    return entities.Weapon(
        name="Silverdawn",
        type="Bow",
        base_atk=674.0,
        secondary_stats={"Crit Damage": 0.441},
        state_rules=state_rules,
        buff_rules=buff_rules,
    )