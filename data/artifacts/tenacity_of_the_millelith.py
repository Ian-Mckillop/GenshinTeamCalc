import engine.entities as entities
import engine.models as models


def build_tenacity_of_the_millelith(pieces: int = 4) -> entities.ArtifactSet:
    """
    Builds Tenacity of the Millelith (Artifact Set).
    - 2-Piece: HP +20%.
    - 4-Piece: When an Elemental Skill hits an opponent, the ATK of all nearby
      party members is increased by 20% and their Shield Strength is increased
      by 30% for 3s. Can be triggered once every 0.5s, even when the equipping
      character is off-field.
    """
    buff_rules = [
        # 2-Piece Bonus: +20% HP
        models.BuffRule(
            buff_id="TENACITY_2PC_HP",
            buff_name="Tenacity of the Millelith 2pc HP%",
            stat="HP%",
            base_value=0.20,
            target_scope="SELF",
        ),
    ]

    state_rules: list[models.StateRule] = []

    if pieces >= 4:
        # Elemental Skill hit by wearer grants/refreshes 3.0s party buff (0.5s trigger ICD, works off-field)
        state_rules.append(
            models.StateRule(
                state_id="Tenacity of the Millelith: 4pc",
                base_duration=3.0,
                trigger_tags=["HIT", "Elemental Skill"],
                trigger_scope="SELF",
                trigger_icd=0.5,
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            )
        )

        buff_rules.extend([
            # 4-Piece Party: +20% ATK for 3s
            models.BuffRule(
                buff_id="TENACITY_4PC_PARTY_ATK",
                buff_name="Tenacity of the Millelith 4pc Party ATK%",
                stat="ATK%",
                base_value=0.20,
                required_states=["Tenacity of the Millelith: 4pc"],
                buff_group="TENACITY_OF_THE_MILLELITH_4PC",
                target_scope="TEAM",
            ),
            # 4-Piece Party: +30% Shield Strength for 3s
            models.BuffRule(
                buff_id="TENACITY_4PC_PARTY_SHIELD_STRENGTH",
                buff_name="Tenacity of the Millelith 4pc Party Shield Strength%",
                stat="Shield Strength%",
                base_value=0.30,
                required_states=["Tenacity of the Millelith: 4pc"],
                buff_group="TENACITY_OF_THE_MILLELITH_4PC_SHIELD",
                target_scope="TEAM",
            ),
        ])

    return entities.ArtifactSet(
        name="Tenacity of the Millelith",
        state_rules=state_rules,
        buff_rules=buff_rules,
    )