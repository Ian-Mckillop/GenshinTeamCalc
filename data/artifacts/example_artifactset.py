import engine.entities as entities
import engine.models as models


def build_example_artifactset(pieces: int = 4) -> entities.ArtifactSet:
    """
    Reference template for building an ArtifactSet in `data/artifacts/`.

    Standard conventions:
    - Function name: `build_<set_snake_case>(pieces: int = 4) -> entities.ArtifactSet`
    - Gate 2-piece effects with `if pieces >= 2:` and 4-piece effects with `if pieces >= 4:`.
    - For 4-piece party buffs that do not stack across multiple wearers, assign a shared
      `buff_group` string (e.g., `buff_group="EXAMPLE_SET_4PC_PARTY"`) and store the
      triggering state with `target_scope="GLOBAL"`.
    - Use `pause_off_field=True` on states whose timers only count down while the
      equipping character is on the field.
    """
    state_rules: list[models.StateRule] = []
    buff_rules: list[models.BuffRule] = []

    if pieces >= 2:
        # 2-Piece Bonus (always active when >= 2 pieces equipped)
        buff_rules.append(
            models.BuffRule(
                buff_id="EXAMPLE_SET_2PC_ATK",
                buff_name="Example Artifact Set 2pc ATK%",
                stat="ATK%",
                base_value=0.18,
                target_scope="SELF",
            )
        )

    if pieces >= 4:
        # Pattern A: Personal sequential stacks that decay 1 stack every 3s while on-field
        state_rules.append(
            models.StateRule(
                state_id="Example Set: Personal Stack",
                base_duration=3.0,
                trigger_tags=["CAST", "Elemental Skill"],
                trigger_scope="SELF",
                stacks=1,
                max_stacks=2,
                refresh_mode="SEQUENTIAL",
                pause_off_field=True,
                target_scope="SELF",
            )
        )

        # Pattern B: Global party-wide buff state (triggers off-field, 0.5s ICD)
        state_rules.append(
            models.StateRule(
                state_id="Example Set: Party Buff",
                base_duration=12.0,
                trigger_tags=["HIT", "Elemental Skill"],
                trigger_scope="SELF",
                trigger_icd=0.5,
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            )
        )

        buff_rules.extend([
            # Personal conditional buff filtered by element & attack/reaction type
            models.BuffRule(
                buff_id="EXAMPLE_SET_4PC_PERSONAL_CR",
                buff_name="Example Artifact Set 4pc Crit Rate",
                stat="Crit Rate",
                base_value=0.20,
                required_states=["Example Set: Personal Stack"],
                target_scope="SELF",
                element_filters=["Cryo"],
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            # Non-stacking party-wide buff (`buff_group` prevents double-application)
            models.BuffRule(
                buff_id="EXAMPLE_SET_4PC_PARTY_ATK",
                buff_name="Example Artifact Set 4pc Party ATK%",
                stat="ATK%",
                base_value=0.20,
                required_states=["Example Set: Party Buff"],
                buff_group="EXAMPLE_ARTIFACT_SET_4PC_PARTY",
                target_scope="TEAM",
            ),
        ])

    return entities.ArtifactSet(
        name="Example Artifact Set",
        state_rules=state_rules,
        buff_rules=buff_rules,
    )