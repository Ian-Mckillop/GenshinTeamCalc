import engine.entities as entities
import engine.models as models


def build_heart_of_the_furnace(pieces: int = 4) -> entities.ArtifactSet:
    """
    Builds Heart of the Furnace (Artifact Set).
    - 2-Piece: ATK +18%.
    - 4-Piece: Increases the equipping character's ATK by 12% for 12s when they
      trigger a Stellar Glimmer reaction or deal Stellar Glimmer reaction DMG.
      Also increases Stellar Glimmer reaction DMG dealt by all nearby party
      members by 50%. Works off-field; the party DMG bonus from multiple sets
      with the same name does not stack.
    """
    buff_rules = [
        # 2-Piece Bonus: +18% ATK
        models.BuffRule(
            buff_id="HEART_OF_THE_FURNACE_2PC_ATK",
            buff_name="Heart of the Furnace 2pc ATK%",
            stat="ATK%",
            base_value=0.18,
            target_scope="SELF",
        ),
    ]

    state_rules: list[models.StateRule] = []

    if pieces >= 4:
        sg_trigger_tag_sets = [
            ["REACTION", "Stellar Glimmer"],
            ["HIT", "Stellar-Conduct"],
            ["HIT", "Stellar Swirl"],
        ]

        for idx, tags in enumerate(sg_trigger_tag_sets, start=1):
            # Personal +12% ATK state (12s, refreshable)
            state_rules.append(
                models.StateRule(
                    state_id="Heart of the Furnace: ATK",
                    base_duration=12.0,
                    trigger_tags=tags,
                    trigger_scope="SELF",
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="SELF",
                )
            )
            # Party +50% Stellar Glimmer DMG state (non-stacking across multiple wearers)
            state_rules.append(
                models.StateRule(
                    state_id="Heart of the Furnace: Party DMG",
                    base_duration=12.0,
                    trigger_tags=tags,
                    trigger_scope="SELF",
                    required_states=["Heart of the Furnace: Party DMG"],
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="TEAM",
                )
            )
            state_rules.append(
                models.StateRule(
                    state_id=f"Heart of the Furnace: Party DMG Activate {idx}",
                    base_duration=0.0,
                    trigger_tags=tags,
                    trigger_scope="SELF",
                    required_states=["!ANY:Heart of the Furnace: Party DMG"],
                    target_scope="SELF",
                )
            )

        # Grant the actual 12s state when `!ANY:Heart of the Furnace: Party DMG` succeeded
        for tags in sg_trigger_tag_sets:
            state_rules.append(
                models.StateRule(
                    state_id="Heart of the Furnace: Party DMG",
                    base_duration=12.0,
                    trigger_tags=tags,
                    trigger_scope="SELF",
                    required_states=["!ANY:Heart of the Furnace: Party DMG"],
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="GLOBAL",
                )
            )

        buff_rules.extend([
            # 4-Piece Personal: +12% ATK for 12s
            models.BuffRule(
                buff_id="HEART_OF_THE_FURNACE_4PC_ATK",
                buff_name="Heart of the Furnace 4pc ATK%",
                stat="ATK%",
                base_value=0.12,
                required_states=["Heart of the Furnace: ATK"],
                target_scope="SELF",
            ),
            # 4-Piece Party: +50% Stellar Glimmer Reaction DMG% (non-stacking)
            models.BuffRule(
                buff_id="HEART_OF_THE_FURNACE_4PC_PARTY_SG_DMG",
                buff_name="Heart of the Furnace 4pc Party Stellar Glimmer DMG%",
                stat="Reaction DMG%",
                base_value=0.50,
                required_states=["Heart of the Furnace: Party DMG"],
                buff_group="HEART_OF_THE_FURNACE_4PC_PARTY",
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
        ])

    return entities.ArtifactSet(
        name="Heart of the Furnace",
        state_rules=state_rules,
        buff_rules=buff_rules,
    )