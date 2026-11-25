import engine.entities as entities
import engine.models as models


def build_silver_light(refinement: int = 1) -> entities.Weapon:
    """
    Builds Silver Light (4-star Sword, Lv. 90, 510 Base ATK, 41.3% ATK).
    Passive — Radiance on the Water (R1–R5):
    - Increases Elemental Mastery by 52 / 65 / 78 / 91 / 104 for 12s after
      Elemental Skill use. Max 2 stacks, each stack's duration is independent.
    """
    r_idx = max(1, min(5, refinement)) - 1
    em_per_stack = 52.0 + 13.0 * r_idx

    state_rules = [
        models.StateRule(
            state_id="Radiance on the Water",
            base_duration=12.0,
            trigger_tags=["CAST", "Elemental Skill"],
            trigger_scope="SELF",
            stacks=1,
            max_stacks=2,
            refresh_mode="INDEPENDENT",
            target_scope="SELF",
        ),
    ]

    buff_rules = [
        # Passive: +52..104 EM per stack (max 2 stacks)
        models.BuffRule(
            buff_id="SILVER_LIGHT_SKILL_EM",
            buff_name="Radiance on the Water EM",
            stat="Elemental Mastery",
            base_value=em_per_stack,
            required_states=["Radiance on the Water"],
            scale_with_stacks=True,
            target_scope="SELF",
        ),
    ]

    return entities.Weapon(
        name="Silver Light",
        type="Sword",
        base_atk=510.0,
        secondary_stats={"ATK%": 0.413},
        state_rules=state_rules,
        buff_rules=buff_rules,
    )