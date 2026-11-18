import engine.entities as entities
import engine.models as models


def _radiance_variants(
    parent_name: str,
    component_name: str,
    normal_mv: float,
    sc_mv: float,
    ss_mv: float,
    normal_type: str,
    base_reqs: list[str],
    hit_offsets: list[float],
    icd_group: str,
    summon_id: str | None = None,
    extra_tags: list[str] | None = None,
) -> list[models.Ability]:
    tags = extra_tags or []
    return [
        models.Ability(
            parent_name=parent_name,
            component_name=component_name,
            mv=normal_mv,
            element="Cryo",
            attack_type=normal_type,
            required_states=[*base_reqs, "!Radiance: Stellar-Conduct", "!Radiance: Stellar Swirl"],
            tags=tags,
            hit_offsets=hit_offsets,
            summon_id=summon_id,
            icd_group=icd_group,
        ),
        models.Ability(
            parent_name=parent_name,
            component_name=f"{component_name} (Stellar-Conduct)",
            mv=sc_mv,
            element="Cryo",
            attack_type="Stellar-Conduct",
            required_states=[*base_reqs, "Radiance: Stellar-Conduct"],
            tags=[*tags, normal_type, "Stellar", "Stellar-Conduct"],
            hit_offsets=hit_offsets,
            summon_id=summon_id,
            icd_group=icd_group,
        ),
        models.Ability(
            parent_name=parent_name,
            component_name=f"{component_name} (Stellar Swirl)",
            mv=ss_mv,
            element="Cryo",
            attack_type="Stellar Swirl",
            required_states=[*base_reqs, "Radiance: Stellar Swirl", "!Radiance: Stellar-Conduct"],
            tags=[*tags, normal_type, "Stellar", "Stellar Swirl"],
            hit_offsets=hit_offsets,
            summon_id=summon_id,
            icd_group=icd_group,
        ),
    ]


def build_anastasya(
    weapon: entities.Weapon,
    constellation: int = 0,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
    sealed_duration: float = 6.0,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    # C3: Burst Lv.10 -> Lv.13; C5: Skill Lv.10 -> Lv.13
    s_scale = (2.125 / 1.8) if constellation >= 5 else 1.0
    b_scale = (2.125 / 1.8) if constellation >= 3 else 1.0

    # C4: Accolades bonuses are 130% of their original values
    acc_mult = 1.30 if constellation >= 4 else 1.0
    acc_cd = 0.12 * acc_mult
    acc_atk = 0.15 * acc_mult
    acc_em = 60.0 * acc_mult

    state_rules = [
        entities.StateRule(state_id="Blessing of Love", base_duration=20.0, trigger_tags=["CAST", "Tap Skill"], termination_rules=["Blessing of Honor"]),
        entities.StateRule(state_id="Palestar Crown", base_duration=20.0, trigger_tags=["CAST", "Tap Skill"], termination_rules=["Blessing of Honor"]),
        entities.StateRule(state_id="Blessing of Honor", base_duration=15.0, trigger_tags=["CAST", "Hold Skill"], termination_rules=["Blessing of Love", "Palestar Crown"]),
        entities.StateRule(state_id="Accolades", base_duration=20.0, trigger_tags=["CAST", "Polestar Skill"]),

        # Love Burst -> Anastasya Seals on swap-out
        entities.StateRule(state_id="To the New World", base_duration=20.0, trigger_tags=["CAST", "Love Burst"], required_states=["Blessing of Love"], freeze_state=["Palestar Crown"]),
        entities.StateRule(state_id="Sealed", base_duration=sealed_duration, trigger_tags=["SWAP_OUT"], required_states=["To the New World", "!Love Seal Used"], target_scope="SELF"),
        entities.StateRule(state_id="Anastasya Accolades Sharing", base_duration=sealed_duration + 8.0, trigger_tags=["SWAP_OUT"], required_states=["To the New World", "!Love Seal Used"], target_scope="SELF"),
        entities.StateRule(state_id="Love Seal Used", base_duration=20.0, trigger_tags=["SWAP_OUT"], required_states=["To the New World", "!Love Seal Used"], target_scope="SELF"),
        entities.StateRule(state_id="Triumph Ready", base_duration=15.0, trigger_tags=["STATE_EXPIRE", "Sealed"], trigger_scope="SELF", target_scope="SELF"),

        # Honor Burst -> Seals up to 3 other teammates
        entities.StateRule(state_id="The Evernight Yields to Dawn", base_duration=14.0, trigger_tags=["CAST", "Honor Burst"], required_states=["Blessing of Honor"], freeze_state=["Blessing of Honor"]),
        entities.StateRule(state_id="Sealed", base_duration=sealed_duration, trigger_tags=["CAST", "Honor Burst"], required_states=["Blessing of Honor"], target_scope="OTHER_TEAMMATES"),
        entities.StateRule(state_id="Teammate Accolades Sharing", base_duration=sealed_duration + 8.0, trigger_tags=["CAST", "Honor Burst"], required_states=["Blessing of Honor"], target_scope="OTHER_TEAMMATES"),
        entities.StateRule(state_id="Doom Ready", base_duration=15.0, trigger_tags=["STATE_EXPIRE", "Sealed"], trigger_scope="OTHER_TEAMMATES", target_scope="SELF"),

        # Edict cast gates
        entities.StateRule(state_id="Triumph Cast", base_duration=1.0, trigger_tags=["CAST", "Triumph"], required_states=["Triumph Ready"], termination_rules=["Triumph Ready"], target_scope="SELF"),
        entities.StateRule(state_id="Doom Cast", base_duration=1.0, trigger_tags=["CAST", "Doom"], required_states=["Doom Ready"], termination_rules=["Doom Ready"], target_scope="SELF"),
    ]

    # A1 Accolades (C1 keeps own Accolades while sharing + triples Anastasya's Sealed shared Accolades)
    own_accolades_reqs = ["Accolades"] if constellation >= 1 else ["Accolades", "!Anastasya Accolades Sharing", "!Teammate Accolades Sharing"]
    buff_rules = [
        entities.BuffRule(buff_id="ANASTASYA_ACCOLADES_OWN_CD", buff_name="Accolades Crit DMG", stat="Crit Damage", base_value=acc_cd, required_states=own_accolades_reqs, target_scope="TEAM"),
        entities.BuffRule(buff_id="ANASTASYA_ACCOLADES_TM_SHARED_CD", buff_name="Teammate Shared Accolades Crit DMG", stat="Crit Damage", base_value=acc_cd, required_states=["ANY:Teammate Accolades Sharing", "Accolades", "!Sealed"], scale_with_stacks=True, party_count_rule="DIVIDE_BY_RECIPIENTS", target_scope="TEAM"),
        entities.BuffRule(buff_id="ANASTASYA_ACCOLADES_ANA_POST_CD", buff_name="Anastasya Post-Seal Shared Accolades Crit DMG", stat="Crit Damage", base_value=acc_cd, required_states=["ANY:Anastasya Accolades Sharing", "!ANY:Sealed", "Accolades", "!Sealed"], scale_with_stacks=True, party_count_rule="DIVIDE_BY_RECIPIENTS", target_scope="TEAM"),
        entities.BuffRule(buff_id="ANASTASYA_ACCOLADES_ANA_SEALED_CD", buff_name="Anastasya Sealed Shared Accolades Crit DMG", stat="Crit Damage", base_value=acc_cd * (3.0 if constellation >= 1 else 1.0), required_states=["ANY:Anastasya Accolades Sharing", "ANY:Sealed", "Accolades", "!Sealed"], scale_with_stacks=True, party_count_rule="DIVIDE_BY_RECIPIENTS", target_scope="TEAM"),

        # A4, P3, Burst DMG%
        entities.BuffRule(buff_id="ANASTASYA_A4_SWIRL", buff_name="Lament for the Lost (Stellar Swirl)", stat="Reaction Base DMG%", base_value=0.15, target_scope="TEAM", ability_filters=["Stellar Swirl"]),
        entities.BuffRule(buff_id="ANASTASYA_P3_ATK_SCALE", buff_name="Stellar Jubilee ATK Scaling", stat="Reaction Base DMG%", base_value=0.00007, scaling_stat="ATK", max_value=0.14, scaling_order=1, target_scope="TEAM", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
        entities.BuffRule(buff_id="ANASTASYA_LOVE_BURST_DMG", buff_name="To the New World Stellar Glimmer DMG%", stat="Reaction DMG%", base_value=0.39 if constellation >= 3 else 0.30, required_states=["To the New World"], target_scope="TEAM", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
    ]

    if constellation >= 1:
        buff_rules.extend([
            entities.BuffRule(buff_id="ANASTASYA_C1_OWN_ATK", buff_name="C1 Accolades Cryo ATK%", stat="ATK%", base_value=acc_atk, required_states=["Accolades"], target_scope="TEAM", char_element_filters=["Cryo"]),
            entities.BuffRule(buff_id="ANASTASYA_C1_OWN_EM", buff_name="C1 Accolades Non-Cryo EM", stat="Elemental Mastery", base_value=acc_em, required_states=["Accolades"], target_scope="TEAM", exclude_char_elements=["Cryo"]),
            entities.BuffRule(buff_id="ANASTASYA_C1_ANA_SEALED_ATK", buff_name="C1 Sealed Shared Accolades ATK%", stat="ATK%", base_value=acc_atk * 3.0, required_states=["ANY:Anastasya Accolades Sharing", "ANY:Sealed", "Accolades", "!Sealed"], scale_with_stacks=True, party_count_rule="DIVIDE_BY_RECIPIENTS", target_scope="TEAM"),
            entities.BuffRule(buff_id="ANASTASYA_C1_ANA_POST_ATK", buff_name="C1 Post-Seal Shared Accolades ATK%", stat="ATK%", base_value=acc_atk, required_states=["ANY:Anastasya Accolades Sharing", "!ANY:Sealed", "Accolades", "!Sealed"], scale_with_stacks=True, party_count_rule="DIVIDE_BY_RECIPIENTS", target_scope="TEAM"),
        ])

    if constellation >= 2:
        state_rules.extend([
            entities.StateRule(state_id="C2 Love Buff", base_duration=30.0, trigger_tags=["CAST", "Tap Skill"]),
            entities.StateRule(state_id="C2 Honor Buff", base_duration=15.0, trigger_tags=["CAST", "Hold Skill"]),
        ])
        buff_rules.extend([
            entities.BuffRule(buff_id="ANASTASYA_C2_LOVE_CD", buff_name="C2 Love Stellar Glimmer Crit DMG", stat="Crit Damage", base_value=0.60, required_states=["C2 Love Buff"], target_scope="TEAM", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
            entities.BuffRule(buff_id="ANASTASYA_C2_HONOR_MULT", buff_name="C2 Honor Original DMG Mult", stat="Original DMG Mult", base_value=1.25, required_states=["C2 Honor Buff"], target_scope="SELF", ability_filters=["Normal Attack", "Honor Burst", "Doom"]),
            entities.BuffRule(buff_id="ANASTASYA_C2_HONOR_ELEV", buff_name="C2 Honor Stellar Glimmer Elevation", stat="Elevation%", base_value=0.05, required_states=["C2 Honor Buff"], target_scope="TEAM", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
        ])

    if constellation >= 6:
        c6_triumph_auto = models.Ability(
            "Palestar Edict: Triumph (C6)", "C6 Auto Triumph", 0.0, element="Cryo", attack_type="Elemental Skill", gauge_units=0.0,
            sub_abilities=[
                models.Ability("Palestar Edict: Triumph (C6)", "C6 Triumph DMG (SC)", round(4.008 * s_scale * 2.50, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct"], hit_offsets=[0.0], icd_group="NONE"),
                models.Ability("Palestar Edict: Triumph (C6)", "C6 Triumph DMG (SS)", round(6.012 * s_scale * 2.50, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl"], hit_offsets=[0.0], icd_group="NONE"),
            ],
        )
        c6_doom3_auto = models.Ability(
            "Palestar Edict: Doom (C6)", "C6 Auto Doom 3-Hit", 0.0, element="Cryo", attack_type="Elemental Skill", gauge_units=0.0,
            sub_abilities=[
                models.Ability("Palestar Edict: Doom (C6)", "C6 Doom 3-Hit (SC)", round(2.806 * s_scale * 2.00, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "C6_DOOM_3"], hit_offsets=[0.0], icd_group="NONE"),
                models.Ability("Palestar Edict: Doom (C6)", "C6 Doom 3-Hit (SS)", round(4.208 * s_scale * 2.00, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl", "C6_DOOM_3"], hit_offsets=[0.0], icd_group="NONE"),
            ],
        )
        state_rules.extend([
            # Love activation on Tap Skill (when not consuming C6 Honor Ready)
            entities.StateRule(state_id="C6 Love Ready", base_duration=30.0, trigger_tags=["CAST", "Tap Skill"], required_states=["!C6 Cooldown", "!C6 Honor Ready"]),
            entities.StateRule(state_id="C6 Love Elevation", base_duration=30.0, trigger_tags=["CAST", "Tap Skill"], required_states=["!C6 Cooldown", "!C6 Honor Ready"]),
            entities.StateRule(state_id="C6 Cooldown", base_duration=15.0, trigger_tags=["CAST", "Tap Skill"], required_states=["!C6 Cooldown", "!C6 Honor Ready"]),
            entities.StateRule(state_id="C6 Love Triggered", base_duration=0.0, trigger_tags=["SWAP_OUT"], required_states=["C6 Love Ready"], termination_rules=["C6 Love Ready"], triggered_ability=c6_triumph_auto),

            # Honor activation on Hold Skill
            entities.StateRule(state_id="C6 Honor Ready", base_duration=30.0, trigger_tags=["CAST", "Hold Skill"], required_states=["!C6 Cooldown"]),
            entities.StateRule(state_id="C6 Honor Elevation", base_duration=30.0, trigger_tags=["CAST", "Hold Skill"], required_states=["!C6 Cooldown"]),
            entities.StateRule(state_id="C6 Cooldown", base_duration=15.0, trigger_tags=["CAST", "Hold Skill"], required_states=["!C6 Cooldown"]),
            entities.StateRule(state_id="C6 Honor Triggered", base_duration=0.0, trigger_tags=["CAST", "Tap Skill"], required_states=["C6 Honor Ready"], termination_rules=["C6 Honor Ready"], triggered_ability=c6_doom3_auto),
            entities.StateRule(state_id="C6 Honor Expire", base_duration=0.0, trigger_tags=["STATE_EXPIRE", "Sealed"], trigger_scope="OTHER_TEAMMATES", termination_rules=["C6 Honor Ready", "C6 Honor Elevation"]),
        ])
        buff_rules.extend([
            entities.BuffRule(buff_id="ANASTASYA_C6_LOVE_ELEV", buff_name="C6 Love Stellar Glimmer Elevation", stat="Elevation%", base_value=0.10, required_states=["C6 Love Elevation"], target_scope="TEAM", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
            entities.BuffRule(buff_id="ANASTASYA_C6_HONOR_ELEV", buff_name="C6 Honor Stellar Glimmer Elevation", stat="Elevation%", base_value=0.20, required_states=["C6 Honor Elevation"], target_scope="SELF", ability_filters=["Stellar-Conduct", "Stellar Swirl"]),
            entities.BuffRule(buff_id="ANASTASYA_C6_FULL_ACCOLADES_CD", buff_name="C6 Full Party Accolades Crit DMG", stat="Crit Damage", base_value=acc_cd * 3.0, required_states=["Accolades", "!ANY:Sealed"], target_scope="SELF", ability_filters=["C6_DOOM_3"]),
            entities.BuffRule(buff_id="ANASTASYA_C6_FULL_ACCOLADES_ATK", buff_name="C6 Full Party Accolades ATK%", stat="ATK%", base_value=acc_atk * 3.0, required_states=["Accolades", "!ANY:Sealed"], target_scope="SELF", ability_filters=["C6_DOOM_3"]),
        ])

    crown_offsets = [2.0 * i for i in range(1, 21)]
    crown_subs = [
        models.Ability("Palestar Crown", "Crown Hit 1", round(1.152 * s_scale, 3), element="Cryo", attack_type="Elemental Skill", required_states=["Palestar Crown"], hit_offsets=crown_offsets, summon_id="palestar_crown", icd_group="CROWN_1"),
        *_radiance_variants("Palestar Crown", "Crown Hit 2", round(1.152 * s_scale, 3), round(0.605 * s_scale, 3), round(0.907 * s_scale, 3), "Elemental Skill", ["Palestar Crown"], crown_offsets, "CROWN_2", summon_id="palestar_crown"),
        models.Ability("Palestar Crown", "Crown Burst Extra (SC)", round(0.202 * b_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Palestar Crown", "To the New World", "!Radiance: Stellar Swirl"], tags=["Elemental Burst", "Stellar", "Stellar-Conduct"], hit_offsets=crown_offsets, summon_id="palestar_crown", icd_group="CROWN_BURST"),
        models.Ability("Palestar Crown", "Crown Burst Extra (SS)", round(0.302 * b_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Palestar Crown", "To the New World", "Radiance: Stellar Swirl"], tags=["Elemental Burst", "Stellar", "Stellar Swirl"], hit_offsets=crown_offsets, summon_id="palestar_crown", icd_group="CROWN_BURST"),
    ]
    abilities = {
        "Skill_Tap": models.Ability("Polestar's Divine Judgment", "Tap Skill DMG", round(2.128 * s_scale, 3), element="Cryo", attack_type="Elemental Skill", tags=["Polestar Skill", "Tap Skill"], hit_offsets=[0.20], cast_duration=0.50, summon_id="palestar_crown", icd_group="NONE", sub_abilities=crown_subs),
        "Skill_Hold": models.Ability("Polestar's Divine Judgment", "Hold Skill DMG", round(2.837 * s_scale, 3), element="Cryo", attack_type="Elemental Skill", tags=["Polestar Skill", "Hold Skill"], hit_offsets=[0.25], cast_duration=0.65, icd_group="NONE"),
        "Spear_N1": models.Ability("Blessed Spear", "1-Hit Cast", 0.0, element="Cryo", attack_type="Normal Attack", required_states=["Blessing of Honor"], cast_duration=0.35, gauge_units=0.0, sub_abilities=_radiance_variants("Blessed Spear", "1-Hit", 1.129, 0.929, 1.393, "Normal Attack", ["Blessing of Honor"], [0.15], "NORMAL")),
        "Burst_Love": models.Ability("To the New World", "Skill DMG", round(3.607 * b_scale, 3), element="Cryo", attack_type="Elemental Burst", required_states=["Blessing of Love"], tags=["Love Burst"], hit_offsets=[0.40], cast_duration=1.20, icd_group="NONE"),
        "Burst_Honor": models.Ability("The Evernight Yields to Dawn", "Burst Cast", 0.0, element="Cryo", attack_type="Elemental Burst", required_states=["Blessing of Honor"], tags=["Honor Burst"], cast_duration=1.20, gauge_units=0.0, sub_abilities=[
            models.Ability("The Evernight Yields to Dawn", "Skill DMG (SC)", round(5.611 * b_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Blessing of Honor", "!Radiance: Stellar Swirl"], tags=["Elemental Burst", "Stellar", "Stellar-Conduct", "Honor Burst"], hit_offsets=[0.40], icd_group="NONE"),
            models.Ability("The Evernight Yields to Dawn", "Skill DMG (SS)", round(8.417 * b_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Blessing of Honor", "Radiance: Stellar Swirl"], tags=["Elemental Burst", "Stellar", "Stellar Swirl", "Honor Burst"], hit_offsets=[0.40], icd_group="NONE"),
        ]),
        "Triumph": models.Ability("Palestar Edict: Triumph", "Triumph Cast", 0.0, element="Cryo", attack_type="Elemental Skill", required_states=["Triumph Ready"], tags=["Triumph"], cast_duration=0.50, gauge_units=0.0, sub_abilities=[
            models.Ability("Palestar Edict: Triumph", "Triumph DMG (SC)", round(4.008 * s_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Triumph Cast", "!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct"], hit_offsets=[0.20], icd_group="NONE"),
            models.Ability("Palestar Edict: Triumph", "Triumph DMG (SS)", round(6.012 * s_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Triumph Cast", "Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl"], hit_offsets=[0.20], icd_group="NONE"),
        ]),
        "Doom": models.Ability("Palestar Edict: Doom", "Doom Cast", 0.0, element="Cryo", attack_type="Elemental Skill", required_states=["Doom Ready"], tags=["Doom"], cast_duration=0.80, gauge_units=0.0, sub_abilities=[
            *[models.Ability("Palestar Edict: Doom", f"Doom Cryo ({i})", round(0.481 * s_scale, 3), element="Cryo", attack_type="Elemental Skill", required_states=["Doom Cast"], tags=["Doom"], hit_offsets=[0.10 + 0.05 * (i - 1)], icd_group="NONE") for i in range(1, 6)],
            models.Ability("Palestar Edict: Doom", "Doom 1-Hit (SC)", round(2.004 * s_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Doom Cast", "!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"], hit_offsets=[0.35], icd_group="NONE"),
            models.Ability("Palestar Edict: Doom", "Doom 1-Hit (SS)", round(3.006 * s_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Doom Cast", "Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"], hit_offsets=[0.35], icd_group="NONE"),
            models.Ability("Palestar Edict: Doom", "Doom 2-Hit (SC)", round(2.405 * s_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Doom Cast", "!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"], hit_offsets=[0.50], icd_group="NONE"),
            models.Ability("Palestar Edict: Doom", "Doom 2-Hit (SS)", round(3.607 * s_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Doom Cast", "Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"], hit_offsets=[0.50], icd_group="NONE"),
            models.Ability("Palestar Edict: Doom", "Doom 3-Hit (SC)", round(2.806 * s_scale, 3), element="Cryo", attack_type="Stellar-Conduct", required_states=["Doom Cast", "!Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"], hit_offsets=[0.65], icd_group="NONE"),
            models.Ability("Palestar Edict: Doom", "Doom 3-Hit (SS)", round(4.208 * s_scale, 3), element="Cryo", attack_type="Stellar Swirl", required_states=["Doom Cast", "Radiance: Stellar Swirl"], tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"], hit_offsets=[0.65], icd_group="NONE"),
        ]),
    }
    anastasya = entities.Character(
        name="Anastasya",
        element="Cryo",
        constellation=constellation,
        base_hp=11200.0,
        base_atk=330.0,
        base_def=720.0,
        weapon=weapon,
        lvl=lvl,
        artifact_set=artifact_set or [],
        ascension_stat={"Crit Damage": 0.384},
        artifact_stats=artifact_stats or {},
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={"Superconduct": "Stellar-Conduct", "Swirl": "Stellar Swirl"},
        polestar_bonus_stacks=1,
        polestar_instant_buff=True,
        instant_lv2_vortex=True,
    )
    return anastasya, abilities