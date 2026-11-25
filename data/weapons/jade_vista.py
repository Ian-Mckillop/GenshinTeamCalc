import engine.entities as entities
import engine.models as models


def build_jade_vista(
    refinement: int = 1,
    same_element_teammates: int = 1,
    diff_element_teammates: int = 2,
) -> entities.Weapon:
    """
    Jade Vista (4-Star Bow)
    Lv. 90/90: 510 Base ATK | 27.6% CRIT Rate

    Passive - A Candle Woven From the Night (R1 -> R5):
    - Per other party member of the same Elemental Type:
      +64 / +80 / +96 / +112 / +128 Elemental Mastery
    - Per other party member of a different Elemental Type:
      +12% / +15% / +18% / +21% / +24% ATK
    - Stacks up to 3 times in total, with Elemental Mastery buffs applied first.
    """
    r_idx = max(1, min(5, refinement)) - 1

    em_per_stack = 64.0 + 16.0 * r_idx
    atk_per_stack = 0.12 + 0.03 * r_idx

    # Enforce 3-stack total cap with Elemental Mastery stacks prioritized first
    em_stacks = max(0, min(3, same_element_teammates))
    atk_stacks = max(0, min(3 - em_stacks, diff_element_teammates))

    buff_rules = []

    if em_stacks > 0:
        buff_rules.append(
            models.BuffRule(
                buff_id="JADE_VISTA_PASSIVE_EM",
                buff_name="Jade Vista Same-Element Elemental Mastery",
                stat="Elemental Mastery",
                base_value=em_per_stack * em_stacks,
                target_scope="SELF",
            )
        )

    if atk_stacks > 0:
        buff_rules.append(
            models.BuffRule(
                buff_id="JADE_VISTA_PASSIVE_ATK",
                buff_name="Jade Vista Different-Element ATK%",
                stat="ATK%",
                base_value=atk_per_stack * atk_stacks,
                target_scope="SELF",
            )
        )

    return entities.Weapon(
        name="Jade Vista",
        type="Bow",
        base_atk=510.0,
        secondary_stats={"Crit Rate": 0.276},
        state_rules=[],
        buff_rules=buff_rules,
    )