import engine.entities as entities
import engine.models as models


def build_ultimate_overlords_mega_magic_sword(
    refinement: int = 5,
    melusine_bonus_ratio: float = 1.0,
) -> entities.Weapon:
    """
    "Ultimate Overlord's Mega Magic Sword" (4-Star Claymore)
    Lv. 90/90: 565 Base ATK | 30.6% Energy Recharge

    Passive - Melussistance! (R1 -> R5):
    - Unconditional ATK%: 12% / 15% / 18% / 21% / 24%
    - Additional ATK% (based on Melusines helped in Merusea Village):
      up to 12% / 15% / 18% / 21% / 24% (`melusine_bonus_ratio` in [0.0, 1.0], defaults to 1.0)
    """
    r_idx = max(1, min(5, refinement)) - 1
    ratio = max(0.0, min(1.0, melusine_bonus_ratio))

    base_atk_bonus = 0.12 + 0.03 * r_idx
    melusine_atk_bonus = (0.12 + 0.03 * r_idx) * ratio

    buff_rules = [
        models.BuffRule(
            buff_id="UOMMS_PASSIVE_BASE_ATK",
            buff_name="Ultimate Overlord's Mega Magic Sword Passive ATK%",
            stat="ATK%",
            base_value=base_atk_bonus,
            target_scope="SELF",
        ),
    ]

    if melusine_atk_bonus > 0:
        buff_rules.append(
            models.BuffRule(
                buff_id="UOMMS_PASSIVE_MELUSINE_ATK",
                buff_name="Ultimate Overlord's Mega Magic Sword Melusine Support ATK%",
                stat="ATK%",
                base_value=melusine_atk_bonus,
                target_scope="SELF",
            )
        )

    return entities.Weapon(
        name='"Ultimate Overlord\'s Mega Magic Sword"',
        type="Claymore",
        base_atk=565.0,
        secondary_stats={"Energy Recharge": 0.306},
        state_rules=[],
        buff_rules=buff_rules,
    )