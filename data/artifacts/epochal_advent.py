import engine.entities as entities
import engine.models as models


def build_epochal_advent(pieces: int = 4) -> entities.ArtifactSet:
    """
    Builds Epochal Advent (Artifact Set)[cite: 20].
    - 2-Piece: ATK +18%[cite: 20].
    - 4-Piece: Gains 1 Starspark (max 2) when using an Elemental Skill, Elemental
      Burst, or performing a Normal Attack[cite: 20]. While holding at least 1 Starspark,
      gains Undying Radiance: +20% CRIT Rate for Cryo DMG, plus an additional
      +20% CRIT Rate if that DMG is Stellar Glimmer reaction DMG[cite: 20]. Loses 1
      Starspark every 3s while on the field; Undying Radiance ends when all
      Starsparks are extinguished[cite: 20].
    """
    buff_rules = [
        # 2-Piece Bonus: +18% ATK
        models.BuffRule(
            buff_id="EPOCHAL_ADVENT_2PC_ATK",
            buff_name="Epochal Advent 2pc ATK%",
            stat="ATK%",
            base_value=0.18,
            target_scope="SELF",
        ),
    ]

    state_rules: list[models.StateRule] = []

    if pieces >= 4:
        # Gain 1 Starspark on Elemental Skill, Elemental Burst, or Normal Attack cast (max 2).
        # `refresh_mode="SEQUENTIAL"` + `base_duration=3.0` + `pause_off_field=True` removes
        # 1 Starspark every 3s while on-field and pauses decay while off-field.
        for trigger_type in ("Elemental Skill", "Elemental Burst", "Normal Attack"):
            state_rules.append(
                models.StateRule(
                    state_id="Epochal Advent: Starspark",
                    base_duration=3.0,
                    trigger_tags=["CAST", trigger_type],
                    trigger_scope="SELF",
                    stacks=1,
                    max_stacks=2,
                    refresh_mode="SEQUENTIAL",
                    pause_off_field=True,
                    target_scope="SELF",
                )
            )

        buff_rules.extend([
            # Undying Radiance Part 1: +20% Crit Rate to Cryo DMG while holding >= 1 Starspark
            models.BuffRule(
                buff_id="EPOCHAL_ADVENT_4PC_CRYO_CR",
                buff_name="Epochal Advent 4pc Cryo Crit Rate",
                stat="Crit Rate",
                base_value=0.20,
                required_states=["Epochal Advent: Starspark"],
                target_scope="SELF",
                element_filters=["Cryo"],
            ),
            # Undying Radiance Part 2: Additional +20% Crit Rate when Cryo DMG is Stellar Glimmer DMG
            models.BuffRule(
                buff_id="EPOCHAL_ADVENT_4PC_SG_CR",
                buff_name="Epochal Advent 4pc Stellar Glimmer Crit Rate",
                stat="Crit Rate",
                base_value=0.20,
                required_states=["Epochal Advent: Starspark"],
                target_scope="SELF",
                element_filters=["Cryo"],
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
        ])

    return entities.ArtifactSet(
        name="Epochal Advent",
        state_rules=state_rules,
        buff_rules=buff_rules,
    )