import engine.entities as entities
import engine.models as models


def build_example_char(
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Standard character blueprint (5-star <Element> <WeaponType>).
    Copy this file to `data/characters/<char_name>.py` and fill in each section.
    """
    # 1. Default Gear & Stat Fallbacks
    if weapon is None:
        weapon = entities.Weapon(name="Dull Blade", type="Sword", base_atk=185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    # 2. Talent Multipliers & Constellation Scaling (Lv. 10 vs Lv. 13 for C3/C5)
    skill_c5 = constellation >= 5
    burst_c3 = constellation >= 3

    na1_mv = 1.000
    na2_mv = 1.100
    na3_mv = 0.750  # x2 multi-hit example
    na4_mv = 1.500
    ca_mv = 1.800
    plunge_low_mv = 2.500
    plunge_high_mv = 3.120

    skill_mv = 2.400 if skill_c5 else 2.000
    summon_tick_mv = 1.200 if skill_c5 else 1.000

    burst_h1_mv = 3.000 if burst_c3 else 2.500
    burst_h2_mv = 4.200 if burst_c3 else 3.500

    # Example constellation-scaled buff values (e.g., C1 amplifies A1/Burst buff)
    a1_atk_bonus = 0.25 if constellation >= 1 else 0.15
    burst_dmg_cap = 500.0 if constellation >= 1 else 350.0

    # 3. Normal, Charged & Plunging Attacks
    # - Add `required_states=["!<Infusion State>"]` if Skill/Burst overrides NAs.
    # - Add `is_blunt=True` on Claymore / blunt attacks so they trigger Shattered on Frozen targets.
    n1 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 1-Hit",
        mv=na1_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    n2 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 2-Hit",
        mv=na2_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    # Multi-hit normal attack pattern: parent container (mv=0.0) + per-hit sub_abilities
    n3_h1 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 3-Hit",
        mv=na3_mv,
        hit_index=1,
        total_hits=2,
        element="Physical",
        attack_type="Normal Attack",
        hit_offsets=[0.15],
    )
    n3_h2 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 3-Hit",
        mv=na3_mv,
        hit_index=2,
        total_hits=2,
        element="Physical",
        attack_type="Normal Attack",
        hit_offsets=[0.28],
    )
    n3 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 3-Hit",
        mv=0.0,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.45,
        gauge_units=0.0,
        sub_abilities=[n3_h1, n3_h2],
    )
    n4 = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Normal 4-Hit",
        mv=na4_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.55,
        hit_offsets=[0.25],
    )
    ca = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Charged Attack",
        mv=ca_mv,
        element="Physical",
        attack_type="Charged Attack",
        cast_duration=0.50,
        hit_offsets=[0.25],
    )
    plunge_low = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="Low Plunge",
        mv=plunge_low_mv,
        element="Physical",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
    )
    plunge_high = models.Ability(
        parent_name="Normal Attack: Example Style",
        component_name="High Plunge",
        mv=plunge_high_mv,
        element="Physical",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
    )

    # 4. Elemental Skill & Summons / Coordinated Attacks
    # Pattern A: Periodic summon ticks (re-casting Skill automatically clears prior future ticks with same summon_id)
    summon_ticks = models.Ability(
        parent_name="Example Skill",
        component_name="Example Summon Tick",
        mv=summon_tick_mv,
        element="Electro",
        attack_type="Elemental Skill",
        required_states=["Example Summon"],
        hit_offsets=[2.0 * i for i in range(1, 7)],  # 6 ticks over 12.0s
        summon_id="example_summon",
        icd_group="EXAMPLE_SUMMON",
    )
    skill = models.Ability(
        parent_name="Example Skill",
        component_name="Skill DMG",
        mv=skill_mv,
        element="Electro",
        attack_type="Elemental Skill",
        tags=["Example Skill"],
        cast_duration=0.50,
        hit_offsets=[0.25],
        summon_id="example_summon",
        icd_group="NONE",
        sub_abilities=[summon_ticks],
    )

    # Pattern B (Optional): Coordinated attack triggered by a StateRule (`triggered_ability=coord_atk`)
    coord_atk = models.Ability(
        parent_name="Example Skill",
        component_name="Coordinated Attack",
        mv=summon_tick_mv,
        element="Electro",
        attack_type="Elemental Skill",
        icd_group="EXAMPLE_COORD",
        hit_offsets=[0.05],
    )

    # 5. Elemental Burst
    burst_h1 = models.Ability(
        parent_name="Example Burst",
        component_name="Burst 1-Hit",
        mv=burst_h1_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.30],
        icd_group="NONE",
    )
    burst_h2 = models.Ability(
        parent_name="Example Burst",
        component_name="Burst 2-Hit",
        mv=burst_h2_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.75],
        icd_group="NONE",
    )
    burst = models.Ability(
        parent_name="Example Burst",
        component_name="Example Burst",
        mv=0.0,
        element="Electro",
        attack_type="Elemental Burst",
        tags=["Example Burst"],
        cast_duration=1.20,
        gauge_units=0.0,
        sub_abilities=[burst_h1, burst_h2],
    )

    # 6. State Rules (Base Kit: Stances, Summons, Passives, Resource Counters)
    # Key StateRule options:
    # - target_scope: "GLOBAL" | "SELF" | "TEAM" | "OTHER_TEAMMATES" | "TRIGGER" | "ON_FIELD"
    # - trigger_scope: "SELF" | "OTHER_TEAMMATES" | "TEAM"
    # - refresh_mode: "REFRESH ALL" | "INDEPENDENT" | "SEQUENTIAL"
    # - trigger_phase: "PRE" (before hit damage, default) | "POST" (after hit damage, for stack consumption)
    # - required_states: supports "!State" (negation), "ANY:State", and "State:N" (minimum N stacks)
    state_rules = [
        models.StateRule(
            state_id="Example Summon",
            base_duration=12.0,
            trigger_tags=["CAST", "Example Skill"],
            target_scope="GLOBAL",
        ),
        models.StateRule(
            state_id="Example Burst Buff",
            base_duration=15.0,
            trigger_tags=["CAST", "Example Burst"],
            target_scope="SELF",
        ),
        # Example A1 passive state triggered by any team reaction
        models.StateRule(
            state_id="Example A1 Synergy",
            base_duration=10.0,
            trigger_tags=["REACTION"],
            trigger_scope="TEAM",
            target_scope="GLOBAL",
        ),
    ]

    # 7. Constellation State Rules (if constellation >= 2 / 4 / 6)
    if constellation >= 2:
        state_rules.append(
            models.StateRule(
                state_id="Example C2 Stack",
                base_duration=15.0,
                trigger_tags=["HIT", "Elemental Skill"],
                max_stacks=3,
                refresh_mode="REFRESH ALL",
                target_scope="SELF",
            )
        )

    # 8. Buff Rules (Base Kit + Constellations)
    # Key BuffRule options:
    # - scaling_order: 0 for flat/percentage stats; 1 for buffs derived from a character's total ATK/HP/DEF/EM
    # - ability_filters / element_filters: restrict buff to specific attack types, tags, or elements
    # - char_element_filters / exclude_char_elements: restrict which teammates receive the buff
    buff_rules = [
        # A1 Passive Buff
        models.BuffRule(
            buff_id="EXAMPLE_A1_TEAM_ATK",
            buff_name="A1 Passive Team ATK%",
            stat="ATK%",
            base_value=a1_atk_bonus,
            required_states=["Example A1 Synergy"],
            target_scope="TEAM",
        ),
        # A4 Passive Stat-Scaling Buff (scaling_order=1 reads character_source's total ATK)
        models.BuffRule(
            buff_id="EXAMPLE_A4_BURST_FLAT_DMG",
            buff_name="A4 Passive Burst Flat DMG",
            stat="Flat DMG",
            base_value=0.20,
            required_states=["Example Burst Buff"],
            scaling_stat="ATK",
            max_value=burst_dmg_cap,
            scaling_order=1,
            target_scope="SELF",
            ability_filters=["Elemental Burst"],
        ),
    ]

    if constellation >= 2:
        buff_rules.append(
            models.BuffRule(
                buff_id="EXAMPLE_C2_CRIT_DMG",
                buff_name="C2 Stackable Crit DMG",
                stat="Crit Damage",
                base_value=0.15,
                required_states=["Example C2 Stack"],
                scale_with_stacks=True,
                target_scope="SELF",
            )
        )

    # 9. Ability Dictionary & Character Assembly
    abilities = {
        "N1": n1,
        "N2": n2,
        "N3": n3,
        "N4": n4,
        "CA": ca,
        "Plunge_Low": plunge_low,
        "Plunge_High": plunge_high,
        "Skill": skill,
        "Burst": burst,
    }

    character = entities.Character(
        name="ExampleChar",
        element="Electro",
        constellation=constellation,
        lvl=lvl,
        base_hp=12500.0,
        base_atk=340.0,
        base_def=780.0,
        weapon=weapon,
        weapon_type="Sword",
        artifact_set=artifact_set,
        ascension_stat={"Crit Rate": 0.192},
        artifact_stats=artifact_stats,
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={},
    )

    return character, abilities