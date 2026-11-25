import engine.entities as entities
import engine.models as models


def build_odette(
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Builds Odette (5-star Cryo Sword) with full C0-C6 kit, passives, and ability dictionary.
    """
    # 1. Default Gear & Stat Fallbacks
    if weapon is None:
        weapon = entities.Weapon(name="Dull Blade", type="Sword", base_atk=185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    # 2. Talent Multipliers & Constellation Scaling (Lv. 10 vs Lv. 13 for C3/C5)
    skill_c3 = constellation >= 3
    burst_c5 = constellation >= 5
    s_scale = 1.18 if skill_c3 else 1.0
    b_scale = 1.18 if burst_c5 else 1.0

    na1_mv = 1.025
    na2_mv = 1.018
    na3_h1_mv = 0.645
    na3_h2_mv = 0.757
    na4_mv = 1.474
    na5_mv = 1.783
    ca_mv = 2.123
    plunge_low_mv = 2.530
    plunge_high_mv = 3.160

    skill_mv = round(1.945 * s_scale, 3)
    coda_dot_mv = round(1.725 * s_scale, 3)
    coda_sc_mv = round(5.500 * s_scale, 3)
    coda_ss_mv = round(8.260 * s_scale, 3)
    plume_mv = round(0.775 * s_scale, 3)
    plume_sc_mv = round(0.490 * s_scale, 3)
    plume_ss_mv = round(0.730 * s_scale, 3)
    wing_mv = round(0.926 * s_scale, 3)
    wing_sc_mv = round(0.580 * s_scale, 3)
    wing_ss_mv = round(0.870 * s_scale, 3)

    burst_slash_mv = round(1.983 * b_scale, 3)
    burst_final_mv = round(3.065 * b_scale, 3)
    snow_swan_dream_bonus = 0.590 if burst_c5 else 0.500

    # A1 Marvelous Splendor stacks & transfer rate (C1 grants +2 stacks & 2 stacks/sec off-field transfer)
    ms_initial_stacks = 6 if constellation >= 1 else 4
    ms_transfer_rate = 2 if constellation >= 1 else 1

    # 3. Normal, Charged & Plunging Attacks (Snow Swan Variation)
    n1 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 1-Hit",
        mv=na1_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    n2 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 2-Hit",
        mv=na2_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    n3_h1 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 3-Hit",
        mv=na3_h1_mv,
        hit_index=1,
        total_hits=2,
        element="Physical",
        attack_type="Normal Attack",
        hit_offsets=[0.15],
    )
    n3_h2 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 3-Hit",
        mv=na3_h2_mv,
        hit_index=2,
        total_hits=2,
        element="Physical",
        attack_type="Normal Attack",
        hit_offsets=[0.28],
    )
    n3 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 3-Hit",
        mv=0.0,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.45,
        gauge_units=0.0,
        sub_abilities=[n3_h1, n3_h2],
    )
    n4 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 4-Hit",
        mv=na4_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.50,
        hit_offsets=[0.22],
    )
    n5 = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Normal 5-Hit",
        mv=na5_mv,
        element="Physical",
        attack_type="Normal Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
    )
    ca = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Charged Attack",
        mv=ca_mv,
        element="Physical",
        attack_type="Charged Attack",
        cast_duration=0.50,
        hit_offsets=[0.25],
    )
    plunge_low = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="Low Plunge",
        mv=plunge_low_mv,
        element="Physical",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
    )
    plunge_high = models.Ability(
        parent_name="Snow Swan Variation",
        component_name="High Plunge",
        mv=plunge_high_mv,
        element="Physical",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
    )

    # 4. Elemental Skill, Solo Dance Double & Special Skill (Adagio: Coda at Dawn's Tolling)
    plume_offsets = [2, 6, 10, 14, 18]
    wing_offsets = [4, 8, 12, 16, 20]

    dance_double_subs = [
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Plume Dance Move",
            mv=plume_mv,
            element="Cryo",
            attack_type="Elemental Skill",
            required_states=["Solo Dance Double"],
            hit_offsets=plume_offsets,
            summon_id="solo_dance_double",
            icd_group="NONE",
            icd_time=0,
        ),
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Plume Dance Move (Stellar-Conduct)",
            mv=plume_sc_mv,
            element="Cryo",
            attack_type="Stellar-Conduct",
            required_states=["Solo Dance Double", "Coda Double Enhanced", "Radiance: Stellar-Conduct"],
            tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
            hit_offsets=plume_offsets,
            summon_id="solo_dance_double",
            gauge_units=0.0,
        ),
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Plume Dance Move (Stellar Swirl)",
            mv=plume_ss_mv,
            element="Cryo",
            attack_type="Stellar Swirl",
            required_states=["Solo Dance Double", "Coda Double Enhanced", "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
            tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
            hit_offsets=plume_offsets,
            summon_id="solo_dance_double",
            gauge_units=0.0,
        ),
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Wing Dance Move",
            mv=wing_mv,
            element="Cryo",
            attack_type="Elemental Skill",
            required_states=["Solo Dance Double"],
            hit_offsets=wing_offsets,
            summon_id="solo_dance_double",
            icd_group="NONE",
        ),
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Wing Dance Move (Stellar-Conduct)",
            mv=wing_sc_mv,
            element="Cryo",
            attack_type="Stellar-Conduct",
            required_states=["Solo Dance Double", "Coda Double Enhanced", "Radiance: Stellar-Conduct"],
            tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
            hit_offsets=wing_offsets,
            summon_id="solo_dance_double",
            gauge_units=0.0
        ),
        models.Ability(
            parent_name="Solo Dance Double",
            component_name="Wing Dance Move (Stellar Swirl)",
            mv=wing_ss_mv,
            element="Cryo",
            attack_type="Stellar Swirl",
            required_states=["Solo Dance Double", "Coda Double Enhanced", "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
            tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
            hit_offsets=wing_offsets,
            summon_id="solo_dance_double",
            gauge_units=0.0
        ),
    ]

    skill = models.Ability(
        parent_name="Adagio: Phantom Night Dancers",
        component_name="Skill DMG",
        mv=skill_mv,
        element="Cryo",
        attack_type="Elemental Skill",
        tags=["Adagio Skill", "Summon Dance Double"],
        cast_duration=0.6667,
        hit_offsets=[0.4167],
        summon_id="solo_dance_double",
        icd_group="NONE",
        sub_abilities=dance_double_subs,
    )

    coda_subs = [
        models.Ability(
            parent_name="Adagio: Coda at Dawn's Tolling",
            component_name="Coda at Dawn's Tolling DoT",
            mv=coda_dot_mv,
            element="Cryo",
            attack_type="Elemental Skill",
            required_states=["Coda Active"],
            hit_offsets=[0.2167, 0.3500, 0.5167],
            icd_group="CODA_DOT",
            icd_time=3,
            icd_hits=999,
        ),
        models.Ability(
            parent_name="Adagio: Coda at Dawn's Tolling",
            component_name="Coda Finale (Stellar-Conduct)",
            mv=coda_sc_mv,
            element="Cryo",
            attack_type="Stellar-Conduct",
            required_states=["Coda Active", "!Radiance: Stellar Swirl"],
            tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
            hit_offsets=[1.0833],
            gauge_units=0.0
        ),
        models.Ability(
            parent_name="Adagio: Coda at Dawn's Tolling",
            component_name="Coda Finale (Stellar Swirl)",
            mv=coda_ss_mv,
            element="Cryo",
            attack_type="Stellar Swirl",
            required_states=["Coda Active", "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
            tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
            hit_offsets=[1.0833],
            gauge_units=0.0
        ),
    ]
    if constellation >= 1:
        coda_subs.extend([
            models.Ability(
                parent_name="Adagio: Coda at Dawn's Tolling",
                component_name="C1 Coda Extra Finale (Stellar-Conduct)",
                mv=3.000,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Coda Active", "!Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
                hit_offsets=[1.50],
                gauge_units=0.0
            ),
            models.Ability(
                parent_name="Adagio: Coda at Dawn's Tolling",
                component_name="C1 Coda Extra Finale (Stellar Swirl)",
                mv=4.500,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Coda Active", "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
                tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
                hit_offsets=[1.50],
                gauge_units=0.0
            ),
        ])

    skill_coda = models.Ability(
        parent_name="Adagio: Coda at Dawn's Tolling",
        component_name="Coda Cast",
        mv=0.0,
        element="Cryo",
        attack_type="Elemental Skill",
        required_states=["Solo Dance Double", "Coda Window"],
        tags=["Coda Skill"],
        cast_duration=1.3667,
        sub_abilities=coda_subs,
    )

    # 5. Elemental Burst (Presto: Bluebird Finale)
    burst_slashes = [
        models.Ability(
            parent_name="Presto: Bluebird Finale",
            component_name=f"Slash {i} DMG",
            mv=burst_slash_mv,
            hit_index=i,
            total_hits=3,
            element="Cryo",
            attack_type="Elemental Burst",
            hit_offsets=[0.25 + 0.15 * (i - 1)],
            icd_group="BURST_SLASH",
        )
        for i in range(1, 4)
    ]
    burst_final = models.Ability(
        parent_name="Presto: Bluebird Finale",
        component_name="Final Slash DMG",
        mv=burst_final_mv,
        element="Cryo",
        attack_type="Elemental Burst",
        hit_offsets=[0.85],
        icd_group="NONE",
    )
    burst = models.Ability(
        parent_name="Presto: Bluebird Finale",
        component_name="Presto: Bluebird Finale",
        mv=0.0,
        element="Cryo",
        attack_type="Elemental Burst",
        tags=["Presto Burst", "Summon Dance Double"],
        cast_duration=1.20,
        gauge_units=0.0,
        summon_id="solo_dance_double",
        sub_abilities=[*burst_slashes, burst_final, *dance_double_subs],
    )

    # 6. State Rules (Solo Dance Double, Coda Window, Snow Swan's Dream, A1 Marvelous Splendor)
    state_rules = [
        # Summon / refresh Solo Dance Double (20.0s, ticks every 1.0s for off-field Marvelous Splendor transfer)
        models.StateRule(
            state_id="Solo Dance Double",
            base_duration=20.1,
            trigger_tags=["CAST", "Summon Dance Double"],
            tick_interval=1.0,
            target_scope="GLOBAL",
        ),
        # Re-summoning Dance Double via Skill resets prior Coda Double enhancement
        models.StateRule(
            state_id="Skill Reset Double Enhancement",
            base_duration=0.0,
            trigger_tags=["CAST", "Adagio Skill"],
            termination_rules=["Coda Double Enhanced"],
            target_scope="SELF",
        ),
        # 6s Coda Window after Skill or Burst
        models.StateRule(
            state_id="Coda Window",
            base_duration=6.0,
            trigger_tags=["CAST", "Summon Dance Double"],
            target_scope="SELF",
        ),
        # Coda Cast Gate & Post-Coda Dance Double Stellar Glimmer Enhancement
        models.StateRule(
            state_id="Coda Active",
            base_duration=2.0,
            trigger_tags=["CAST", "Coda Skill"],
            required_states=["Solo Dance Double", "Coda Window"],
            termination_rules=["Coda Window"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Coda Double Enhanced",
            base_duration=20.0,
            trigger_tags=["CAST", "Coda Skill"],
            required_states=["Solo Dance Double", "Coda Window"],
            target_scope="SELF",
        ),
        # Burst Snow Swan's Dream (20.0s)
        models.StateRule(
            state_id="Snow Swan's Dream",
            base_duration=20.0,
            trigger_tags=["CAST", "Presto Burst"],
            target_scope="SELF",
        ),
        # A1: Marvelous Splendor (4 stacks at C0, 6 at C1; refreshes to full cap when Dance Double is summoned)
        models.StateRule(
            state_id="Marvelous Splendor",
            base_duration=20.0,
            trigger_tags=["CAST", "Summon Dance Double"],
            stacks=ms_initial_stacks,
            max_stacks=ms_initial_stacks,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Clear Teammate Marvelous Splendor",
            base_duration=0.0,
            trigger_tags=["CAST", "Summon Dance Double"],
            termination_rules=["Marvelous Splendor"],
            target_scope="OTHER_TEAMMATES",
        ),
        # Track Odette's off-field status
        models.StateRule(
            state_id="Odette Off-Field",
            base_duration=float("inf"),
            trigger_tags=["SWAP_OUT"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Odette On-Field",
            base_duration=0.0,
            trigger_tags=["SWAP_IN"],
            termination_rules=["Odette Off-Field"],
            target_scope="SELF",
        ),
        # Off-field transfer: every 1.0s while Odette is off-field, teammates gain stacks (up to cap)
        models.StateRule(
            state_id="Marvelous Splendor",
            base_duration=20.0,
            trigger_tags=["STATE_TICK", "Solo Dance Double"],
            required_states=["Odette Off-Field", "Marvelous Splendor"],
            stacks=ms_transfer_rate,
            max_stacks=ms_initial_stacks,
            refresh_mode="REFRESH ALL",
            target_scope="OTHER_TEAMMATES",
        ),
        # Cleanup Marvelous Splendor & Coda Double Enhanced when Solo Dance Double expires
        models.StateRule(
            state_id="Dance Double Expire Cleanup",
            base_duration=0.0,
            trigger_tags=["STATE_EXPIRE", "Solo Dance Double"],
            termination_rules=["Marvelous Splendor", "Coda Double Enhanced"],
            target_scope="TEAM",
        ),
    ]

    # At C0-C5, Odette loses stacks as she transfers them off-field; at C6 her own stacks do not decrease
    if constellation < 6:
        state_rules.append(
            models.StateRule(
                state_id="Marvelous Splendor Off-Field Decay",
                base_duration=0.0,
                trigger_tags=["STATE_TICK", "Solo Dance Double"],
                required_states=["Odette Off-Field", "Marvelous Splendor"],
                consume_stacks={"Marvelous Splendor": ms_transfer_rate},
                target_scope="SELF",
            )
        )

    # 7. Constellation State Rules
    if constellation >= 4:
        c4_coord_atk = models.Ability(
            parent_name="Up, Up the Long, Delirious, Burning Blue (C4)",
            component_name="C4 Coordinated Attack",
            mv=0.0,
            element="Cryo",
            attack_type="Elemental Skill",
            gauge_units=0.0,
            sub_abilities=[
                models.Ability(
                    parent_name="Up, Up the Long, Delirious, Burning Blue (C4)",
                    component_name="C4 Coordinated Attack (SC)",
                    mv=0.660,
                    element="Cryo",
                    attack_type="Stellar-Conduct",
                    required_states=["!Radiance: Stellar Swirl"],
                    tags=["Stellar", "Stellar-Conduct"],
                    hit_offsets=[0.05],
                    icd_group="NONE",
                ),
                models.Ability(
                    parent_name="Up, Up the Long, Delirious, Burning Blue (C4)",
                    component_name="C4 Coordinated Attack (SS)",
                    mv=0.990,
                    element="Cryo",
                    attack_type="Stellar Swirl",
                    required_states=["Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
                    tags=["Stellar", "Stellar Swirl"],
                    hit_offsets=[0.05],
                    icd_group="NONE",
                ),
            ],
        )
        state_rules.extend([
            models.StateRule(
                state_id="Odette C4 Coord Trigger",
                base_duration=0.0,
                trigger_tags=["HIT", "Stellar"],
                trigger_icd=3.5,
                trigger_scope="TEAM",
                target_scope="SELF",
                triggered_ability=c4_coord_atk,
            ),
            models.StateRule(
                state_id="Odette C4 Coord Trigger",
                base_duration=0.0,
                trigger_tags=["REACTION", "Stellar Glimmer"],
                trigger_icd=3.5,
                trigger_scope="TEAM",
                target_scope="SELF",
                triggered_ability=c4_coord_atk,
            ),
        ])

    # 8. Buff Rules (Base Kit + Constellations)
    buff_rules = [
        # A1: Marvelous Splendor (+15% Stellar Glimmer Reaction DMG% per stack)
        models.BuffRule(
            buff_id="ODETTE_A1_MARVELOUS_SPLENDOR_DMG",
            buff_name="Marvelous Splendor Stellar Glimmer DMG%",
            stat="Reaction DMG%",
            base_value=0.15,
            required_states=["Marvelous Splendor"],
            scale_with_stacks=True,
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # A4: Pathetique of Pateticheskaya (+1.5% Original DMG per 100 ATK over 1,000, max +30%)
        models.BuffRule(
            buff_id="ODETTE_A4_ORIGINAL_DMG",
            buff_name="Pathetique of Pateticheskaya Stellar Glimmer Original DMG",
            stat="Original DMG Mult",
            base_value=0.00015,
            scaling_stat="ATK",
            scaling_offset=1000.0,
            max_value=0.30,
            scaling_order=3,
            target_scope="SELF",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # P3: Stellar Jubilee (Base Stellar-Conduct / Stellar Swirl DMG +0.7% per 100 ATK, max 14%)
        models.BuffRule(
            buff_id="ODETTE_P3_ATK_SCALE",
            buff_name="Stellar Jubilee ATK Scaling",
            stat="Reaction Base DMG%",
            base_value=0.00007,
            scaling_stat="ATK",
            max_value=0.14,
            scaling_order=3,
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # Burst: Snow Swan's Dream (+50% / +59% Stellar Glimmer Reaction DMG% for Odette)
        models.BuffRule(
            buff_id="ODETTE_BURST_SNOW_SWAN_DREAM",
            buff_name="Snow Swan's Dream Stellar Glimmer DMG%",
            stat="Reaction DMG%",
            base_value=snow_swan_dream_bonus,
            required_states=["Snow Swan's Dream"],
            target_scope="SELF",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    if constellation >= 2:
        buff_rules.extend([
            models.BuffRule(
                buff_id="ODETTE_C2_MARVELOUS_SPLENDOR_ATK",
                buff_name="C2 Marvelous Splendor ATK%",
                stat="ATK%",
                base_value=0.07,
                required_states=["Marvelous Splendor"],
                scale_with_stacks=True,
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="ODETTE_C2_SC_CRYO_ELECTRO_SHRED",
                buff_name="C2 Dance Double Stellar-Conduct Cryo/Electro RES Shred",
                stat="RES Shred",
                base_value=0.20,
                required_states=["Solo Dance Double", "Radiance: Stellar-Conduct"],
                target_scope="TEAM",
                element_filters=["Cryo", "Electro"],
            ),
            models.BuffRule(
                buff_id="ODETTE_C2_SS_CRYO_ANEMO_SHRED",
                buff_name="C2 Dance Double Stellar Swirl Cryo/Anemo RES Shred",
                stat="RES Shred",
                base_value=0.20,
                required_states=["Solo Dance Double", "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
                target_scope="TEAM",
                element_filters=["Cryo", "Anemo"],
            ),
        ])

    if constellation >= 4:
        buff_rules.append(
            models.BuffRule(
                buff_id="ODETTE_C4_TEAM_SNOW_SWAN_DREAM",
                buff_name="C4 Team Snow Swan's Dream Stellar Glimmer DMG%",
                stat="Reaction DMG%",
                base_value=snow_swan_dream_bonus * 0.50,
                required_states=["ANY:Snow Swan's Dream"],
                target_scope="OTHER_TEAMMATES",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            )
        )

    if constellation >= 6:
        buff_rules.extend([
            models.BuffRule(
                buff_id="ODETTE_C6_TEAM_MS_ELEVATION",
                buff_name="C6 Marvelous Splendor Stellar Glimmer Elevation",
                stat="Elevation",
                base_value=0.25,
                required_states=["Marvelous Splendor"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            models.BuffRule(
                buff_id="ODETTE_C6_SELF_MS_ELEVATION",
                buff_name="C6 Odette Additional Stellar Glimmer Elevation",
                stat="Elevation",
                base_value=0.20,
                required_states=["Marvelous Splendor"],
                target_scope="SELF",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
        ])

    # 9. Ability Dictionary & Character Assembly
    abilities = {
        "N1": n1,
        "N2": n2,
        "N3": n3,
        "N4": n4,
        "N5": n5,
        "CA": ca,
        "Plunge_Low": plunge_low,
        "Plunge_High": plunge_high,
        "Skill": skill,
        "Skill_Coda": skill_coda,
        "Burst": burst,
    }

    odette = entities.Character(
        name="Odette",
        element="Cryo",
        constellation=constellation,
        lvl=lvl,
        base_hp=12981.0,
        base_atk=335.0,
        base_def=787.0,
        weapon=weapon,
        weapon_type="Sword",
        artifact_set=artifact_set,
        ascension_stat={"Crit Damage": 0.384},
        artifact_stats=artifact_stats,
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={"Superconduct": "Stellar-Conduct", "Swirl": "Stellar Swirl"},
    )

    return odette, abilities