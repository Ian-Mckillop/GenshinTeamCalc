import engine.entities as entities
import engine.models as models


def build_yae_miko(
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Builds Yae Miko (5-star Electro Catalyst) with full C0-C6 kit, passives
    (including Hexerei / Edict of Cleansing), and ability dictionary.
    """
    # 1. Default Gear & Stat Fallbacks
    if weapon is None:
        weapon = entities.Weapon(name="Apprentice's Notes", type="Catalyst", base_atk=185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    # 2. Talent Multipliers & Constellation Scaling (Lv. 10 vs Lv. 13 for C3/C5)
    skill_c3 = constellation >= 3
    burst_c5 = constellation >= 5

    na1_mv = 0.714
    na2_mv = 0.693
    na3_mv = 1.024
    ca_mv = 2.572
    plunge_low_mv = 2.250
    plunge_high_mv = 2.810

    sakura_lv1_mv = 1.289 if skill_c3 else 1.092
    sakura_lv2_mv = 1.611 if skill_c3 else 1.365
    sakura_lv3_mv = 2.014 if skill_c3 else 1.706
    sakura_lv4_mv = 2.518 if skill_c3 else 2.133

    # C2 (Fox's Mooncall): Sesshou Sakura start at Level 2 and max at Level 4
    if constellation >= 2:
        totem_1_mv = sakura_lv2_mv
        totem_2_mv = sakura_lv3_mv
        totem_3_mv = sakura_lv4_mv
    else:
        totem_1_mv = sakura_lv1_mv
        totem_2_mv = sakura_lv2_mv
        totem_3_mv = sakura_lv3_mv

    burst_skill_mv = 5.520 if burst_c5 else 4.680
    tenko_bolt_mv = 7.090 if burst_c5 else 6.010

    # 3. Normal, Charged & Plunging Attacks (Spiritfox Sin-Eater)
    n1 = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="Normal 1-Hit",
        mv=na1_mv,
        element="Electro",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    n2 = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="Normal 2-Hit",
        mv=na2_mv,
        element="Electro",
        attack_type="Normal Attack",
        cast_duration=0.35,
        hit_offsets=[0.15],
    )
    n3 = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="Normal 3-Hit",
        mv=na3_mv,
        element="Electro",
        attack_type="Normal Attack",
        cast_duration=0.45,
        hit_offsets=[0.20],
    )
    ca = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="Charged Attack",
        mv=ca_mv,
        element="Electro",
        attack_type="Charged Attack",
        cast_duration=0.60,
        hit_offsets=[0.35],
        icd_group="NONE",
    )
    plunge_low = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="Low Plunge",
        mv=plunge_low_mv,
        element="Electro",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
        icd_group="NONE",
    )
    plunge_high = models.Ability(
        parent_name="Spiritfox Sin-Eater",
        component_name="High Plunge",
        mv=plunge_high_mv,
        element="Electro",
        attack_type="Plunging Attack",
        cast_duration=0.60,
        hit_offsets=[0.30],
        icd_group="NONE",
    )

    # 4. Elemental Skill: Yakan Evocation: Sesshou Sakura (24.0s duration with Edict of Cleansing)
    # Each totem ticks every 2.8s (8 strikes over 24.0s); MV dynamically scales with active totem count.
    sakura_tick_offsets = [2.8, 5.6, 8.4, 11.2, 14, 16.8, 19.6, 22.4]

    def make_sakura_skill(slot_idx: int) -> models.Ability:
        s_id = f"sesshou_sakura_{slot_idx}"
        subs = [
            models.Ability(
                parent_name="Yakan Evocation: Sesshou Sakura",
                component_name=f"Sesshou Sakura {slot_idx} Strike (1-Totem)",
                mv=totem_1_mv,
                element="Electro",
                attack_type="Elemental Skill",
                tags=["Sesshou Sakura"],
                required_states=["Sesshou Sakura:1", "!Sesshou Sakura:2"],
                hit_offsets=sakura_tick_offsets,
                summon_id=s_id,
                icd_group="SESSHOU_SAKURA",
            ),
            models.Ability(
                parent_name="Yakan Evocation: Sesshou Sakura",
                component_name=f"Sesshou Sakura {slot_idx} Strike (2-Totem)",
                mv=totem_2_mv,
                element="Electro",
                attack_type="Elemental Skill",
                tags=["Sesshou Sakura"],
                required_states=["Sesshou Sakura:2", "!Sesshou Sakura:3"],
                hit_offsets=sakura_tick_offsets,
                summon_id=s_id,
                icd_group="SESSHOU_SAKURA",
            ),
            models.Ability(
                parent_name="Yakan Evocation: Sesshou Sakura",
                component_name=f"Sesshou Sakura {slot_idx} Strike (3-Totem)",
                mv=totem_3_mv,
                element="Electro",
                attack_type="Elemental Skill",
                tags=["Sesshou Sakura"],
                required_states=["Sesshou Sakura:3"],
                hit_offsets=sakura_tick_offsets,
                summon_id=s_id,
                icd_group="SESSHOU_SAKURA",
            ),
        ]
        return models.Ability(
            parent_name="Yakan Evocation: Sesshou Sakura",
            component_name=f"Sesshou Sakura Cast {slot_idx}",
            mv=0.0,
            element="Electro",
            attack_type="Elemental Skill",
            tags=["Yakan Skill"],
            cast_duration=0.35,
            gauge_units=0.0,
            summon_id=s_id,
            sub_abilities=subs,
        )

    skill_1 = make_sakura_skill(1)
    skill_2 = make_sakura_skill(2)
    skill_3 = make_sakura_skill(3)

    # 5. Elemental Burst: Great Secret Art: Tenko Kenshin
    # Consumes all active Sesshou Sakura (1, 2, or 3) to unleash 1 Tenko Thunderbolt per totem.
    burst_subs = [
        models.Ability(
            parent_name="Great Secret Art: Tenko Kenshin",
            component_name="Skill DMG",
            mv=burst_skill_mv,
            element="Electro",
            attack_type="Elemental Burst",
            hit_offsets=[0.40],
            icd_group="NONE",
        ),
        models.Ability(
            parent_name="Great Secret Art: Tenko Kenshin",
            component_name="Tenko Thunderbolt 1",
            mv=tenko_bolt_mv,
            element="Electro",
            attack_type="Elemental Burst",
            required_states=["Tenko Bolts Pending:1"],
            hit_offsets=[0.80],
            icd_group="NONE",
        ),
        models.Ability(
            parent_name="Great Secret Art: Tenko Kenshin",
            component_name="Tenko Thunderbolt 2",
            mv=tenko_bolt_mv,
            element="Electro",
            attack_type="Elemental Burst",
            required_states=["Tenko Bolts Pending:2"],
            hit_offsets=[1.05],
            icd_group="NONE",
        ),
        models.Ability(
            parent_name="Great Secret Art: Tenko Kenshin",
            component_name="Tenko Thunderbolt 3",
            mv=tenko_bolt_mv,
            element="Electro",
            attack_type="Elemental Burst",
            required_states=["Tenko Bolts Pending:3"],
            hit_offsets=[1.30],
            icd_group="NONE",
        ),
    ]
    burst = models.Ability(
        parent_name="Great Secret Art: Tenko Kenshin",
        component_name="Great Secret Art: Tenko Kenshin",
        mv=0.0,
        element="Electro",
        attack_type="Elemental Burst",
        tags=["Tenko Burst"],
        cast_duration=1.50,
        gauge_units=0.0,
        sub_abilities=burst_subs,
    )

    # 6. Triggered Abilities for Passives (A1 & P3 Edict of Cleansing)
    a1_strike_normal = models.Ability(
        parent_name="The Shrine's Sacred Shade (A1)",
        component_name="A1 Additional Lightning Strike",
        mv=0.400,
        element="Electro",
        attack_type="Elemental Skill",
        required_states=["!Radiance: Stellar-Conduct"],
        hit_offsets=[0.05],
        gauge_units=0.0,
    )
    a1_strike_sc = models.Ability(
        parent_name="The Shrine's Sacred Shade (A1)",
        component_name="A1 Additional Lightning Strike (Stellar-Conduct)",
        mv=0.500,
        element="Electro",
        attack_type="Stellar-Conduct",
        required_states=["Radiance: Stellar-Conduct"],
        tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
        hit_offsets=[0.05],
        gauge_units=0.0,
    )

    p3_edict_sc_bolt = models.Ability(
        parent_name="Edict of Cleansing (P3)",
        component_name="Edict Enhanced Bolt (Stellar-Conduct)",
        mv=2.000,
        element="Electro",
        attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
        hit_offsets=[0.05],
        gauge_units=0.0,
    )

    # 7. State Rules (Sesshou Sakura Stacks, Burst Conversion, A1, P3 Edict of Cleansing)
    state_rules = [
        # Track active Sesshou Sakura count (up to 3, 24.0s duration with Edict of Cleansing)
        models.StateRule(
            state_id="Sesshou Sakura",
            base_duration=24.0,
            trigger_tags=["CAST", "Yakan Skill"],
            max_stacks=3,
            refresh_mode="INDEPENDENT",
            target_scope="GLOBAL",
        ),
        # A1: When there are already 3 Sesshou Sakura active, unleashing Skill fires an extra strike (4th+ cast)
        models.StateRule(
            state_id="Yae A1 3-Totem Strike",
            base_duration=0.0,
            trigger_tags=["CAST", "Yakan Skill"],
            required_states=["Sesshou Sakura:3"],
            target_scope="SELF",
            triggered_ability=a1_strike_normal,
        ),
        models.StateRule(
            state_id="Yae A1 3-Totem Strike SC",
            base_duration=0.0,
            trigger_tags=["CAST", "Yakan Skill"],
            required_states=["Sesshou Sakura:3", "Radiance: Stellar-Conduct"],
            target_scope="SELF",
            triggered_ability=a1_strike_sc,
        ),
        # Burst transforms up to 3 active Sesshou Sakura into Tenko Thunderbolts and clears the totems
        models.StateRule(
            state_id="Tenko Bolts Pending",
            base_duration=2.0,
            trigger_tags=["CAST", "Tenko Burst"],
            required_states=["Sesshou Sakura:1"],
            stacks=1,
            max_stacks=3,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Tenko Bolts Pending",
            base_duration=2.0,
            trigger_tags=["CAST", "Tenko Burst"],
            required_states=["Sesshou Sakura:2"],
            stacks=1,
            max_stacks=3,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Tenko Bolts Pending",
            base_duration=2.0,
            trigger_tags=["CAST", "Tenko Burst"],
            required_states=["Sesshou Sakura:3"],
            stacks=1,
            max_stacks=3,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Consume Sesshou Sakura",
            base_duration=0.0,
            trigger_tags=["CAST", "Tenko Burst"],
            termination_rules=["Sesshou Sakura"],
            target_scope="GLOBAL",
        ),
        # P3 (Edict of Cleansing): Team Superconduct or Stellar-Conduct enhances next Sesshou Sakura strike (2.5s CD)
        models.StateRule(
            state_id="Edict Enhanced Sakura",
            base_duration=24.0,
            trigger_tags=["REACTION", "Superconduct"],
            required_states=["!Edict Enhanced Sakura"],
            trigger_scope="TEAM",
            trigger_icd=2.5,
            max_stacks=1,
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Edict Enhanced Sakura",
            base_duration=24.0,
            trigger_tags=["REACTION", "Stellar-Conduct"],
            required_states=["!Edict Enhanced Sakura"],
            trigger_scope="TEAM",
            trigger_icd=2.5,
            max_stacks=1,
            target_scope="SELF",
        ),
        # P3 Radiance: Stellar-Conduct bonus 200% ATK Stellar-Conduct strike on enhanced Sakura hit
        models.StateRule(
            state_id="Edict Bolt Fired",
            base_duration=0.05,
            trigger_tags=["HIT", "Sesshou Sakura"],
            required_states=["Edict Enhanced Sakura", "Radiance: Stellar-Conduct"],
            target_scope="SELF",
            triggered_ability=p3_edict_sc_bolt,
        ),
        # Consume Edict Enhanced Sakura in POST only if it was actually used on this strike
        models.StateRule(
            state_id="Consume Edict Enhanced Sakura",
            base_duration=0.0,
            trigger_tags=["HIT", "Sesshou Sakura"],
            trigger_phase="POST",
            required_states=["Edict Enhanced Sakura", "Edict Bolt Fired"],
            consume_stacks={"Edict Enhanced Sakura": 1},
            termination_rules=["Edict Bolt Fired"],
            target_scope="SELF",
        ),
        # Track Yae Miko's off-field status (for C2 active-character EM sharing)
        models.StateRule(
            state_id="Yae Off-Field",
            base_duration=float("inf"),
            trigger_tags=["SWAP_OUT"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Yae On-Field",
            base_duration=0.0,
            trigger_tags=["SWAP_IN"],
            termination_rules=["Yae Off-Field"],
            target_scope="SELF",
        ),
    ]

    # 8. Constellation State Rules
    if constellation >= 1:
        # C1: Yae triggers Superconduct/Stellar-Conduct or deals Stellar-Conduct DMG -> +50% Electro & SC DMG% for 10s
        for c1_tags in (
            ["REACTION", "Superconduct"],
            ["REACTION", "Stellar-Conduct"],
            ["HIT", "Stellar-Conduct"],
        ):
            state_rules.append(
                models.StateRule(
                    state_id="Yakan Offering C1",
                    base_duration=10.0,
                    trigger_tags=c1_tags,
                    trigger_scope="SELF",
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="TEAM",
                )
            )

    if constellation >= 4:
        # C4: Sesshou Sakura hit grants +20% Electro DMG Bonus to party for 5s
        state_rules.append(
            models.StateRule(
                state_id="Sakura Channeling C4",
                base_duration=5.0,
                trigger_tags=["HIT", "Sesshou Sakura"],
                trigger_scope="SELF",
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            )
        )

    # 9. Buff Rules (Base Kit + Constellations)
    buff_rules = [
        # A4: Enlightened Blessing (+0.15% Sesshou Sakura DMG% per point of EM)
        models.BuffRule(
            buff_id="YAE_A4_EM_TO_SAKURA_DMG",
            buff_name="Enlightened Blessing Sesshou Sakura DMG%",
            stat="Elemental Skill DMG%",
            base_value=0.0015,
            scaling_stat="Elemental Mastery",
            scaling_order=1,
            target_scope="SELF",
            ability_filters=["Sesshou Sakura"],
        ),
        # P3: Edict of Cleansing (+80% ATK Flat DMG on enhanced Sesshou Sakura strike)
        models.BuffRule(
            buff_id="YAE_P3_EDICT_FLAT_DMG",
            buff_name="Edict of Cleansing Enhanced Sakura Flat DMG",
            stat="Flat DMG",
            base_value=0.80,
            required_states=["Edict Enhanced Sakura"],
            scaling_stat="ATK",
            scaling_order=1,
            target_scope="SELF",
            ability_filters=["Sesshou Sakura"],
        ),
    ]

    if constellation >= 1:
        buff_rules.extend([
            models.BuffRule(
                buff_id="YAE_C1_ELECTRO_DMG",
                buff_name="Yakan Offering C1 Electro DMG%",
                stat="Electro DMG%",
                base_value=0.50,
                required_states=["Yakan Offering C1"],
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="YAE_C1_STELLAR_CONDUCT_DMG",
                buff_name="Yakan Offering C1 Stellar-Conduct DMG%",
                stat="Reaction DMG%",
                base_value=0.50,
                required_states=["Yakan Offering C1"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct"],
            ),
        ])

    if constellation >= 2:
        # C2: Sesshou Sakura grants 90 / 120 / 200 EM (Lv. 2 / 3 / 4) to Yae Miko & active character
        c2_em_tiers = [
            ("C2_LV2", 90.0, ["Sesshou Sakura:1", "!Sesshou Sakura:2"]),
            ("C2_LV3", 120.0, ["Sesshou Sakura:2", "!Sesshou Sakura:3"]),
            ("C2_LV4", 200.0, ["Sesshou Sakura:3"]),
        ]
        for tag, em_val, reqs in c2_em_tiers:
            buff_rules.append(
                models.BuffRule(
                    buff_id=f"YAE_{tag}_SELF_EM",
                    buff_name=f"Fox's Mooncall ({tag}) Yae EM",
                    stat="Elemental Mastery",
                    base_value=em_val,
                    required_states=reqs,
                    target_scope="SELF",
                )
            )
            buff_rules.append(
                models.BuffRule(
                    buff_id=f"YAE_{tag}_ON_FIELD_EM",
                    buff_name=f"Fox's Mooncall ({tag}) Active Teammate EM",
                    stat="Elemental Mastery",
                    base_value=em_val,
                    required_states=["Yae Off-Field", *reqs],
                    target_scope="ON_FIELD",
                )
            )

    if constellation >= 4:
        buff_rules.extend([
            models.BuffRule(
                buff_id="YAE_C4_PARTY_ELECTRO_DMG",
                buff_name="Sakura Channeling C4 Party Electro DMG%",
                stat="Electro DMG%",
                base_value=0.20,
                required_states=["Sakura Channeling C4"],
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="YAE_C4_SELF_BURST_DMG",
                buff_name="Sakura Channeling C4 Burst DMG%",
                stat="Elemental Burst DMG%",
                base_value=1.00,
                target_scope="SELF",
            ),
        ])

    if constellation >= 6:
        buff_rules.extend([
            models.BuffRule(
                buff_id="YAE_C6_SAKURA_DEF_IGNORE",
                buff_name="Forbidden Art: Daisesshou C6 Sakura DEF Ignore",
                stat="DEF Ignore",
                base_value=0.60,
                target_scope="SELF",
                ability_filters=["Sesshou Sakura"],
            ),
            models.BuffRule(
                buff_id="YAE_C6_STELLAR_CONDUCT_CD",
                buff_name="Forbidden Art: Daisesshou C6 Stellar-Conduct Crit DMG",
                stat="Crit Damage",
                base_value=2.00,
                target_scope="SELF",
                ability_filters=["Stellar-Conduct"],
            ),
        ])

    # 10. Ability Dictionary & Character Assembly
    abilities = {
        "N1": n1,
        "N2": n2,
        "N3": n3,
        "CA": ca,
        "Plunge_Low": plunge_low,
        "Plunge_High": plunge_high,
        "Skill": skill_1,
        "Skill_1": skill_1,
        "Skill_2": skill_2,
        "Skill_3": skill_3,
        "Burst": burst,
    }

    yae = entities.Character(
        name="Yae Miko",
        element="Electro",
        constellation=constellation,
        lvl=lvl,
        base_hp=10372.0,
        base_atk=340.0,
        base_def=569.0,
        weapon=weapon,
        weapon_type="Catalyst",
        artifact_set=artifact_set,
        ascension_stat={"Crit Rate": 0.192},
        artifact_stats=artifact_stats,
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={},
    )

    return yae, abilities