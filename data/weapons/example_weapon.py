import engine.entities as entities
import engine.models as models


def build_example_weapon(refinement: int = 1) -> entities.Weapon:
    """
    Reference template for building a Weapon in `data/weapons/`.

    Standard conventions:
    - Function name: `build_<weapon_snake_case>(refinement: int = 1) -> entities.Weapon`
    - Clamp refinement to [1, 5] and compute `r_idx = max(1, min(5, refinement)) - 1`.
    - Put the weapon's secondary stat (ATK%, Crit Rate, Crit Damage, Elemental Mastery,
      HP%, DEF%, Energy Recharge%) as a permanent `BuffRule` with `target_scope="SELF"`.
    - Use `target_scope="GLOBAL"` on a `StateRule` whenever a `TEAM` or `ON_FIELD`
      `BuffRule` checks `required_states=[...]`, so teammates can read the state.
    """
    r_idx = max(1, min(5, refinement)) - 1

    # Refinement scaling (R1 -> R5)
    unconditional_atk = 0.16 + 0.04 * r_idx       # 16% / 20% / 24% / 28% / 32%
    stack_em = 40.0 + 10.0 * r_idx                # 40 / 50 / 60 / 70 / 80 per stack
    team_sg_dmg = 0.20 + 0.05 * r_idx             # 20% / 25% / 30% / 35% / 40%
    em_to_dmg_ratio = 0.0004 + 0.0001 * r_idx     # 0.04%..0.08% DMG% per 1 EM

    state_rules = [
        # Pattern A: Independent stacking personal state (e.g., on Elemental Skill cast)
        models.StateRule(
            state_id="Example Weapon: Stack",
            base_duration=12.0,
            trigger_tags=["CAST", "Elemental Skill"],
            trigger_scope="SELF",
            stacks=1,
            max_stacks=2,
            refresh_mode="INDEPENDENT",  # Options: "REFRESH ALL", "INDEPENDENT", "SEQUENTIAL"
            target_scope="SELF",
        ),
        # Pattern B: Global state triggered by wearer's hit/reaction (works off-field)
        models.StateRule(
            state_id="Example Weapon: Party Aura",
            base_duration=15.0,
            trigger_tags=["REACTION", "Stellar Glimmer"],
            trigger_scope="SELF",
            trigger_icd=0.5,
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
    ]

    buff_rules = [
        # 1. Weapon Secondary Stat (Lv. 90)
        models.BuffRule(
            buff_id="EXAMPLE_WEAPON_SUBSTAT_CR",
            buff_name="Example Weapon Substat Crit Rate",
            stat="Crit Rate",
            base_value=0.331,
            target_scope="SELF",
        ),
        # 2. Unconditional Passive Stat
        models.BuffRule(
            buff_id="EXAMPLE_WEAPON_PASSIVE_ATK",
            buff_name="Example Weapon Passive ATK%",
            stat="ATK%",
            base_value=unconditional_atk,
            target_scope="SELF",
        ),
        # 3. Stack-Scaling Passive Buff
        models.BuffRule(
            buff_id="EXAMPLE_WEAPON_STACK_EM",
            buff_name="Example Weapon Stack Elemental Mastery",
            stat="Elemental Mastery",
            base_value=stack_em,
            required_states=["Example Weapon: Stack"],
            scale_with_stacks=True,
            target_scope="SELF",
        ),
        # 4. Active / Team Conditional Buff (filtered to specific reaction/attack types)
        models.BuffRule(
            buff_id="EXAMPLE_WEAPON_ON_FIELD_SG_DMG",
            buff_name="Example Weapon Active Stellar Glimmer DMG%",
            stat="Reaction DMG%",
            base_value=team_sg_dmg,
            required_states=["Example Weapon: Party Aura"],
            target_scope="ON_FIELD",  # Options: "SELF", "ON_FIELD", "TEAM", "OTHER_TEAMMATES"
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # 5. Dynamic Stat-Conversion Buff (`scaling_order=1` runs after flat/percent stats)
        models.BuffRule(
            buff_id="EXAMPLE_WEAPON_EM_TO_DMG",
            buff_name="Example Weapon EM to Elemental DMG%",
            stat="DMG%",
            base_value=em_to_dmg_ratio,
            scaling_stat="Elemental Mastery",
            scaling_offset=0.0,
            max_value=0.40,
            scaling_order=1,
            target_scope="SELF",
            element_filters=["Cryo", "Electro"],
        ),
    ]

    return entities.Weapon(
        name="Example Weapon",
        type="Sword",  # Options: "Sword", "Claymore", "Polearm", "Bow", "Catalyst"
        base_atk=608.0,
        state_rules=state_rules,
        buff_rules=buff_rules,
    )