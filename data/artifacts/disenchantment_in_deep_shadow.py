import engine.entities as entities
import engine.models as models


def build_disenchantment_in_deep_shadow(pieces: int = 4) -> entities.ArtifactSet:
    """
    Builds Disenchantment in Deep Shadow (Artifact Set).
    - 2-Piece: ATK +18%.
    - 4-Piece: Increases Superconduct Reaction DMG by 80% and Stellar-Conduct
      Reaction DMG by 40%. When the wielder attacks opponents affected by
      Superconduct or Stellar-Conduct, this attack's CRIT Rate is increased by 16%.
    """
    buff_rules = [
        # 2-Piece Bonus: +18% ATK
        models.BuffRule(
            buff_id="DISENCHANTMENT_2PC_ATK",
            buff_name="Disenchantment in Deep Shadow 2pc ATK%",
            stat="ATK%",
            base_value=0.18,
            target_scope="SELF",
        ),
    ]

    state_rules: list[models.StateRule] = []

    if pieces >= 4:
        # Track when opponents are affected by Superconduct (12s) or Stellar-Conduct (6s Polestar Field)
        state_rules.extend([
            models.StateRule(
                state_id="Disenchantment: Conduct Affected",
                base_duration=12.0,
                trigger_tags=["REACTION", "Superconduct"],
                trigger_scope="TEAM",
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            ),
            models.StateRule(
                state_id="Disenchantment: Conduct Affected",
                base_duration=6.0,
                trigger_tags=["REACTION", "Stellar-Conduct"],
                trigger_scope="TEAM",
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            ),
        ])

        buff_rules.extend([
            # 4-Piece: +80% Superconduct Reaction DMG%
            models.BuffRule(
                buff_id="DISENCHANTMENT_4PC_SUPERCONDUCT_DMG",
                buff_name="Disenchantment in Deep Shadow 4pc Superconduct DMG%",
                stat="Reaction DMG%",
                base_value=0.80,
                target_scope="SELF",
                ability_filters=["Superconduct"],
            ),
            # 4-Piece: +40% Stellar-Conduct Reaction DMG%
            models.BuffRule(
                buff_id="DISENCHANTMENT_4PC_STELLAR_CONDUCT_DMG",
                buff_name="Disenchantment in Deep Shadow 4pc Stellar-Conduct DMG%",
                stat="Reaction DMG%",
                base_value=0.40,
                target_scope="SELF",
                ability_filters=["Stellar-Conduct"],
            ),
            # 4-Piece: +16% Crit Rate against opponents affected by Superconduct or Stellar-Conduct
            models.BuffRule(
                buff_id="DISENCHANTMENT_4PC_CRIT_RATE",
                buff_name="Disenchantment in Deep Shadow 4pc Crit Rate",
                stat="Crit Rate",
                base_value=0.16,
                required_states=["Disenchantment: Conduct Affected"],
                target_scope="SELF",
            ),
        ])

    return entities.ArtifactSet(
        name="Disenchantment in Deep Shadow",
        state_rules=state_rules,
        buff_rules=buff_rules,
    )