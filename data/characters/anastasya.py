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
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
    sealed_duration: float = 6.0,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Builds Anastasya (5-star Cryo Bow) with full C0-C6 kit, passives, and ability dictionary.
    """
    if weapon is None:
        weapon = entities.Weapon(name="Hunter's Bow", type="Bow", base_atk=185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    skill_c5 = constellation >= 5
    burst_c3 = constellation >= 3

    # --- Talent Multipliers (Lv. 10 vs Lv. 13 for C3/C5) ---
    s_scale = (2.125 / 1.8) if skill_c5 else 1.0
    b_scale = (2.125 / 1.8) if burst_c3 else 1.0

    skill_tap_mv = round(2.128 * s_scale, 3)
    skill_hold_mv = round(2.837 * s_scale, 3)
    crown_h1_mv = round(1.152 * s_scale, 3)
    crown_h2_mv = round(1.152 * s_scale, 3)
    crown_h2_sc_mv = round(0.605 * s_scale, 3)
    crown_h2_ss_mv = round(0.907 * s_scale, 3)

    triumph_sc_mv = round(4.008 * s_scale, 3)
    triumph_ss_mv = round(6.012 * s_scale, 3)
    doom_cryo_mv = round(0.481 * s_scale, 3)
    doom_h1_sc_mv = round(2.004 * s_scale, 3)
    doom_h1_ss_mv = round(3.006 * s_scale, 3)
    doom_h2_sc_mv = round(2.405 * s_scale, 3)
    doom_h2_ss_mv = round(3.607 * s_scale, 3)
    doom_h3_sc_mv = round(2.806 * s_scale, 3)
    doom_h3_ss_mv = round(4.208 * s_scale, 3)

    c6_triumph_sc_mv = round(4.008 * s_scale * 2.50, 3)
    c6_triumph_ss_mv = round(6.012 * s_scale * 2.50, 3)
    c6_doom3_sc_mv = round(2.806 * s_scale * 2.00, 3)
    c6_doom3_ss_mv = round(4.208 * s_scale * 2.00, 3)

    burst_love_mv = round(3.607 * b_scale, 3)
    burst_honor_sc_mv = round(5.611 * b_scale, 3)
    burst_honor_ss_mv = round(8.417 * b_scale, 3)
    crown_burst_sc_mv = round(0.202 * b_scale, 3)
    crown_burst_ss_mv = round(0.302 * b_scale, 3)

    # A1 / C1 / C4 Accolades & Love Burst Scaling
    acc_mult = 1.30 if constellation >= 4 else 1.0
    acc_cd = 0.12 * acc_mult
    acc_atk = 0.15 * acc_mult
    acc_em = 60.0 * acc_mult
    love_burst_dmg_bonus = 0.39 if burst_c3 else 0.30

    # --- Blessed Spear Infused Normal Attacks ---
    spear_n1 = models.Ability(
        parent_name="Blessed Spear",
        component_name="1-Hit Cast",
        mv=0.0,
        element="Cryo",
        attack_type="Normal Attack",
        required_states=["Blessing of Honor"],
        cast_duration=0.35,
        gauge_units=0.0,
        sub_abilities=_radiance_variants(
            parent_name="Blessed Spear",
            component_name="1-Hit",
            normal_mv=1.129,
            sc_mv=0.929,
            ss_mv=1.393,
            normal_type="Normal Attack",
            base_reqs=["Blessing of Honor"],
            hit_offsets=[0.15],
            icd_group="NORMAL",
        ),
    )

    # --- Elemental Skill & Palestar Crown ---
    crown_offsets = [2.0 * i for i in range(1, 21)]
    crown_subs = [
        models.Ability(
            parent_name="Palestar Crown",
            component_name="Crown Hit 1",
            mv=crown_h1_mv,
            element="Cryo",
            attack_type="Elemental Skill",
            required_states=["Palestar Crown"],
            hit_offsets=crown_offsets,
            summon_id="palestar_crown",
            icd_group="CROWN_1",
        ),
        *_radiance_variants(
            parent_name="Palestar Crown",
            component_name="Crown Hit 2",
            normal_mv=crown_h2_mv,
            sc_mv=crown_h2_sc_mv,
            ss_mv=crown_h2_ss_mv,
            normal_type="Elemental Skill",
            base_reqs=["Palestar Crown"],
            hit_offsets=crown_offsets,
            icd_group="CROWN_2",
            summon_id="palestar_crown",
        ),
        models.Ability(
            parent_name="Palestar Crown",
            component_name="Crown Burst Extra (SC)",
            mv=crown_burst_sc_mv,
            element="Cryo",
            attack_type="Stellar-Conduct",
            required_states=["Palestar Crown", "To the New World", "!Radiance: Stellar Swirl"],
            tags=["Elemental Burst", "Stellar", "Stellar-Conduct"],
            hit_offsets=crown_offsets,
            summon_id="palestar_crown",
            icd_group="CROWN_BURST",
        ),
        models.Ability(
            parent_name="Palestar Crown",
            component_name="Crown Burst Extra (SS)",
            mv=crown_burst_ss_mv,
            element="Cryo",
            attack_type="Stellar Swirl",
            required_states=["Palestar Crown", "To the New World", "Radiance: Stellar Swirl"],
            tags=["Elemental Burst", "Stellar", "Stellar Swirl"],
            hit_offsets=crown_offsets,
            summon_id="palestar_crown",
            icd_group="CROWN_BURST",
        ),
    ]

    skill_tap = models.Ability(
        parent_name="Polestar's Divine Judgment",
        component_name="Tap Skill DMG",
        mv=skill_tap_mv,
        element="Cryo",
        attack_type="Elemental Skill",
        tags=["Polestar Skill", "Tap Skill"],
        cast_duration=0.50,
        hit_offsets=[0.20],
        summon_id="palestar_crown",
        icd_group="NONE",
        sub_abilities=crown_subs,
    )
    skill_hold = models.Ability(
        parent_name="Polestar's Divine Judgment",
        component_name="Hold Skill DMG",
        mv=skill_hold_mv,
        element="Cryo",
        attack_type="Elemental Skill",
        tags=["Polestar Skill", "Hold Skill"],
        cast_duration=0.65,
        hit_offsets=[0.25],
        icd_group="NONE",
    )

    # --- Elemental Bursts ---
    burst_love = models.Ability(
        parent_name="To the New World",
        component_name="Skill DMG",
        mv=burst_love_mv,
        element="Cryo",
        attack_type="Elemental Burst",
        required_states=["Blessing of Love"],
        tags=["Love Burst"],
        cast_duration=1.20,
        hit_offsets=[0.40],
        icd_group="NONE",
    )
    burst_honor = models.Ability(
        parent_name="The Evernight Yields to Dawn",
        component_name="Burst Cast",
        mv=0.0,
        element="Cryo",
        attack_type="Elemental Burst",
        required_states=["Blessing of Honor"],
        tags=["Honor Burst"],
        cast_duration=1.20,
        gauge_units=0.0,
        sub_abilities=[
            models.Ability(
                parent_name="The Evernight Yields to Dawn",
                component_name="Skill DMG (SC)",
                mv=burst_honor_sc_mv,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Blessing of Honor", "!Radiance: Stellar Swirl"],
                tags=["Elemental Burst", "Stellar", "Stellar-Conduct", "Honor Burst"],
                hit_offsets=[0.40],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="The Evernight Yields to Dawn",
                component_name="Skill DMG (SS)",
                mv=burst_honor_ss_mv,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Blessing of Honor", "Radiance: Stellar Swirl"],
                tags=["Elemental Burst", "Stellar", "Stellar Swirl", "Honor Burst"],
                hit_offsets=[0.40],
                icd_group="NONE",
            ),
        ],
    )

    # --- Palestar Edicts (Triumph & Doom) ---
    triumph = models.Ability(
        parent_name="Palestar Edict: Triumph",
        component_name="Triumph Cast",
        mv=0.0,
        element="Cryo",
        attack_type="Elemental Skill",
        required_states=["Triumph Ready"],
        tags=["Triumph"],
        cast_duration=0.50,
        gauge_units=0.0,
        sub_abilities=[
            models.Ability(
                parent_name="Palestar Edict: Triumph",
                component_name="Triumph DMG (SC)",
                mv=triumph_sc_mv,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Triumph Cast", "!Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
                hit_offsets=[0.20],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Triumph",
                component_name="Triumph DMG (SS)",
                mv=triumph_ss_mv,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Triumph Cast", "Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
                hit_offsets=[0.20],
                icd_group="NONE",
            ),
        ],
    )

    doom_cryo_hits = [
        models.Ability(
            parent_name="Palestar Edict: Doom",
            component_name=f"Doom Cryo ({i})",
            mv=doom_cryo_mv,
            element="Cryo",
            attack_type="Elemental Skill",
            required_states=["Doom Cast"],
            tags=["Doom"],
            hit_offsets=[0.10 + 0.05 * (i - 1)],
            icd_group="NONE",
        )
        for i in range(1, 6)
    ]
    doom = models.Ability(
        parent_name="Palestar Edict: Doom",
        component_name="Doom Cast",
        mv=0.0,
        element="Cryo",
        attack_type="Elemental Skill",
        required_states=["Doom Ready"],
        tags=["Doom"],
        cast_duration=0.80,
        gauge_units=0.0,
        sub_abilities=[
            *doom_cryo_hits,
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 1-Hit (SC)",
                mv=doom_h1_sc_mv,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Doom Cast", "!Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"],
                hit_offsets=[0.35],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 1-Hit (SS)",
                mv=doom_h1_ss_mv,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Doom Cast", "Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"],
                hit_offsets=[0.35],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 2-Hit (SC)",
                mv=doom_h2_sc_mv,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Doom Cast", "!Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"],
                hit_offsets=[0.50],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 2-Hit (SS)",
                mv=doom_h2_ss_mv,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Doom Cast", "Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"],
                hit_offsets=[0.50],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 3-Hit (SC)",
                mv=doom_h3_sc_mv,
                element="Cryo",
                attack_type="Stellar-Conduct",
                required_states=["Doom Cast", "!Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Doom"],
                hit_offsets=[0.65],
                icd_group="NONE",
            ),
            models.Ability(
                parent_name="Palestar Edict: Doom",
                component_name="Doom 3-Hit (SS)",
                mv=doom_h3_ss_mv,
                element="Cryo",
                attack_type="Stellar Swirl",
                required_states=["Doom Cast", "Radiance: Stellar Swirl"],
                tags=["Elemental Skill", "Stellar", "Stellar Swirl", "Doom"],
                hit_offsets=[0.65],
                icd_group="NONE",
            ),
        ],
    )

    # --- State Rules ---
    state_rules = [
        # Skill Stances & Accolades
        models.StateRule(
            state_id="Blessing of Love",
            base_duration=20.0,
            trigger_tags=["CAST", "Tap Skill"],
            termination_rules=["Blessing of Honor"],
        ),
        models.StateRule(
            state_id="Palestar Crown",
            base_duration=20.0,
            trigger_tags=["CAST", "Tap Skill"],
            termination_rules=["Blessing of Honor"],
        ),
        models.StateRule(
            state_id="Blessing of Honor",
            base_duration=15.0,
            trigger_tags=["CAST", "Hold Skill"],
            termination_rules=["Blessing of Love", "Palestar Crown"],
        ),
        models.StateRule(
            state_id="Accolades",
            base_duration=20.0,
            trigger_tags=["CAST", "Polestar Skill"],
        ),
        # Love Burst -> Anastasya Seals on swap-out
        models.StateRule(
            state_id="To the New World",
            base_duration=20.0,
            trigger_tags=["CAST", "Love Burst"],
            required_states=["Blessing of Love"],
            freeze_state=["Palestar Crown"],
        ),
        models.StateRule(
            state_id="Sealed",
            base_duration=sealed_duration,
            trigger_tags=["SWAP_OUT"],
            required_states=["To the New World", "!Love Seal Used"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Anastasya Accolades Sharing",
            base_duration=sealed_duration + 8.0,
            trigger_tags=["SWAP_OUT"],
            required_states=["To the New World", "!Love Seal Used"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Love Seal Used",
            base_duration=20.0,
            trigger_tags=["SWAP_OUT"],
            required_states=["To the New World", "!Love Seal Used"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Triumph Ready",
            base_duration=15.0,
            trigger_tags=["STATE_EXPIRE", "Sealed"],
            trigger_scope="SELF",
            target_scope="SELF",
        ),
        # Honor Burst -> Seals up to 3 other teammates
        models.StateRule(
            state_id="The Evernight Yields to Dawn",
            base_duration=14.0,
            trigger_tags=["CAST", "Honor Burst"],
            required_states=["Blessing of Honor"],
            freeze_state=["Blessing of Honor"],
        ),
        models.StateRule(
            state_id="Sealed",
            base_duration=sealed_duration,
            trigger_tags=["CAST", "Honor Burst"],
            required_states=["Blessing of Honor"],
            target_scope="OTHER_TEAMMATES",
        ),
        models.StateRule(
            state_id="Teammate Accolades Sharing",
            base_duration=sealed_duration + 8.0,
            trigger_tags=["CAST", "Honor Burst"],
            required_states=["Blessing of Honor"],
            target_scope="OTHER_TEAMMATES",
        ),
        models.StateRule(
            state_id="Doom Ready",
            base_duration=15.0,
            trigger_tags=["STATE_EXPIRE", "Sealed"],
            trigger_scope="OTHER_TEAMMATES",
            target_scope="SELF",
        ),
        # Edict Cast Gates
        models.StateRule(
            state_id="Triumph Cast",
            base_duration=1.0,
            trigger_tags=["CAST", "Triumph"],
            required_states=["Triumph Ready"],
            termination_rules=["Triumph Ready"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Doom Cast",
            base_duration=1.0,
            trigger_tags=["CAST", "Doom"],
            required_states=["Doom Ready"],
            termination_rules=["Doom Ready"],
            target_scope="SELF",
        ),
    ]

    # --- Constellation State Rules ---
    if constellation >= 2:
        state_rules.extend([
            models.StateRule(
                state_id="C2 Love Buff",
                base_duration=30.0,
                trigger_tags=["CAST", "Tap Skill"],
            ),
            models.StateRule(
                state_id="C2 Honor Buff",
                base_duration=15.0,
                trigger_tags=["CAST", "Hold Skill"],
            ),
        ])

    if constellation >= 6:
        c6_triumph_auto = models.Ability(
            parent_name="Palestar Edict: Triumph (C6)",
            component_name="C6 Auto Triumph",
            mv=0.0,
            element="Cryo",
            attack_type="Elemental Skill",
            gauge_units=0.0,
            sub_abilities=[
                models.Ability(
                    parent_name="Palestar Edict: Triumph (C6)",
                    component_name="C6 Triumph DMG (SC)",
                    mv=c6_triumph_sc_mv,
                    element="Cryo",
                    attack_type="Stellar-Conduct",
                    required_states=["!Radiance: Stellar Swirl"],
                    tags=["Elemental Skill", "Stellar", "Stellar-Conduct"],
                    hit_offsets=[0.0],
                    icd_group="NONE",
                ),
                models.Ability(
                    parent_name="Palestar Edict: Triumph (C6)",
                    component_name="C6 Triumph DMG (SS)",
                    mv=c6_triumph_ss_mv,
                    element="Cryo",
                    attack_type="Stellar Swirl",
                    required_states=["Radiance: Stellar Swirl"],
                    tags=["Elemental Skill", "Stellar", "Stellar Swirl"],
                    hit_offsets=[0.0],
                    icd_group="NONE",
                ),
            ],
        )
        c6_doom3_auto = models.Ability(
            parent_name="Palestar Edict: Doom (C6)",
            component_name="C6 Auto Doom 3-Hit",
            mv=0.0,
            element="Cryo",
            attack_type="Elemental Skill",
            gauge_units=0.0,
            sub_abilities=[
                models.Ability(
                    parent_name="Palestar Edict: Doom (C6)",
                    component_name="C6 Doom 3-Hit (SC)",
                    mv=c6_doom3_sc_mv,
                    element="Cryo",
                    attack_type="Stellar-Conduct",
                    required_states=["!Radiance: Stellar Swirl"],
                    tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "C6_DOOM_3"],
                    hit_offsets=[0.0],
                    icd_group="NONE",
                ),
                models.Ability(
                    parent_name="Palestar Edict: Doom (C6)",
                    component_name="C6 Doom 3-Hit (SS)",
                    mv=c6_doom3_ss_mv,
                    element="Cryo",
                    attack_type="Stellar Swirl",
                    required_states=["Radiance: Stellar Swirl"],
                    tags=["Elemental Skill", "Stellar", "Stellar Swirl", "C6_DOOM_3"],
                    hit_offsets=[0.0],
                    icd_group="NONE",
                ),
            ],
        )
        state_rules.extend([
            # Love activation on Tap Skill (when not consuming C6 Honor Ready)
            models.StateRule(
                state_id="C6 Love Ready",
                base_duration=30.0,
                trigger_tags=["CAST", "Tap Skill"],
                required_states=["!C6 Cooldown", "!C6 Honor Ready"],
            ),
            models.StateRule(
                state_id="C6 Love Elevation",
                base_duration=30.0,
                trigger_tags=["CAST", "Tap Skill"],
                required_states=["!C6 Cooldown", "!C6 Honor Ready"],
            ),
            models.StateRule(
                state_id="C6 Cooldown",
                base_duration=15.0,
                trigger_tags=["CAST", "Tap Skill"],
                required_states=["!C6 Cooldown", "!C6 Honor Ready"],
            ),
            models.StateRule(
                state_id="C6 Love Triggered",
                base_duration=0.0,
                trigger_tags=["SWAP_OUT"],
                required_states=["C6 Love Ready"],
                termination_rules=["C6 Love Ready"],
                triggered_ability=c6_triumph_auto,
            ),
            # Honor activation on Hold Skill
            models.StateRule(
                state_id="C6 Honor Ready",
                base_duration=30.0,
                trigger_tags=["CAST", "Hold Skill"],
                required_states=["!C6 Cooldown"],
            ),
            models.StateRule(
                state_id="C6 Honor Elevation",
                base_duration=30.0,
                trigger_tags=["CAST", "Hold Skill"],
                required_states=["!C6 Cooldown"],
            ),
            models.StateRule(
                state_id="C6 Cooldown",
                base_duration=15.0,
                trigger_tags=["CAST", "Hold Skill"],
                required_states=["!C6 Cooldown"],
            ),
            models.StateRule(
                state_id="C6 Honor Triggered",
                base_duration=0.0,
                trigger_tags=["CAST", "Tap Skill"],
                required_states=["C6 Honor Ready"],
                termination_rules=["C6 Honor Ready"],
                triggered_ability=c6_doom3_auto,
            ),
            models.StateRule(
                state_id="C6 Honor Expire",
                base_duration=0.0,
                trigger_tags=["STATE_EXPIRE", "Sealed"],
                trigger_scope="OTHER_TEAMMATES",
                termination_rules=["C6 Honor Ready", "C6 Honor Elevation"],
            ),
        ])

    # --- Buff Rules ---
    own_accolades_reqs = (
        ["Accolades"]
        if constellation >= 1
        else ["Accolades", "!Anastasya Accolades Sharing", "!Teammate Accolades Sharing"]
    )
    buff_rules = [
        # A1: Accolades Sharing (C1 keeps own Accolades while sharing & triples Sealed shared Accolades)
        models.BuffRule(
            buff_id="ANASTASYA_ACCOLADES_OWN_CD",
            buff_name="Accolades Crit DMG",
            stat="Crit Damage",
            base_value=acc_cd,
            required_states=own_accolades_reqs,
            target_scope="TEAM",
        ),
        models.BuffRule(
            buff_id="ANASTASYA_ACCOLADES_TM_SHARED_CD",
            buff_name="Teammate Shared Accolades Crit DMG",
            stat="Crit Damage",
            base_value=acc_cd,
            required_states=["ANY:Teammate Accolades Sharing", "Accolades", "!Sealed"],
            scale_with_stacks=True,
            party_count_rule="DIVIDE_BY_RECIPIENTS",
            target_scope="TEAM",
        ),
        models.BuffRule(
            buff_id="ANASTASYA_ACCOLADES_ANA_POST_CD",
            buff_name="Anastasya Post-Seal Shared Accolades Crit DMG",
            stat="Crit Damage",
            base_value=acc_cd,
            required_states=["ANY:Anastasya Accolades Sharing", "!ANY:Sealed", "Accolades", "!Sealed"],
            scale_with_stacks=True,
            party_count_rule="DIVIDE_BY_RECIPIENTS",
            target_scope="TEAM",
        ),
        models.BuffRule(
            buff_id="ANASTASYA_ACCOLADES_ANA_SEALED_CD",
            buff_name="Anastasya Sealed Shared Accolades Crit DMG",
            stat="Crit Damage",
            base_value=acc_cd * (3.0 if constellation >= 1 else 1.0),
            required_states=["ANY:Anastasya Accolades Sharing", "ANY:Sealed", "Accolades", "!Sealed"],
            scale_with_stacks=True,
            party_count_rule="DIVIDE_BY_RECIPIENTS",
            target_scope="TEAM",
        ),
        # A4: Lament for the Lost (+15% Base Stellar Swirl DMG)
        models.BuffRule(
            buff_id="ANASTASYA_A4_SWIRL",
            buff_name="Lament for the Lost (Stellar Swirl)",
            stat="Reaction Base DMG%",
            base_value=0.15,
            target_scope="TEAM",
            ability_filters=["Stellar Swirl"],
        ),
        # P3: Stellar Jubilee (Base Stellar-Conduct / Stellar Swirl DMG +0.7% per 100 ATK, max 14%)
        models.BuffRule(
            buff_id="ANASTASYA_P3_ATK_SCALE",
            buff_name="Stellar Jubilee ATK Scaling",
            stat="Reaction Base DMG%",
            base_value=0.00007,
            scaling_stat="ATK",
            max_value=0.14,
            scaling_order=1,
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # Elemental Burst: To the New World Stellar Glimmer DMG%
        models.BuffRule(
            buff_id="ANASTASYA_LOVE_BURST_DMG",
            buff_name="To the New World Stellar Glimmer DMG%",
            stat="Reaction DMG%",
            base_value=love_burst_dmg_bonus,
            required_states=["To the New World"],
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    if constellation >= 1:
        buff_rules.extend([
            models.BuffRule(
                buff_id="ANASTASYA_C1_OWN_ATK",
                buff_name="C1 Accolades Cryo ATK%",
                stat="ATK%",
                base_value=acc_atk,
                required_states=["Accolades"],
                target_scope="TEAM",
                char_element_filters=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C1_OWN_EM",
                buff_name="C1 Accolades Non-Cryo EM",
                stat="Elemental Mastery",
                base_value=acc_em,
                required_states=["Accolades"],
                target_scope="TEAM",
                exclude_char_elements=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C1_ANA_SEALED_ATK",
                buff_name="C1 Sealed Shared Accolades ATK%",
                stat="ATK%",
                base_value=acc_atk * 3.0,
                required_states=["ANY:Anastasya Accolades Sharing", "ANY:Sealed", "Accolades", "!Sealed"],
                scale_with_stacks=True,
                party_count_rule="DIVIDE_BY_RECIPIENTS",
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C1_ANA_POST_ATK",
                buff_name="C1 Post-Seal Shared Accolades ATK%",
                stat="ATK%",
                base_value=acc_atk,
                required_states=["ANY:Anastasya Accolades Sharing", "!ANY:Sealed", "Accolades", "!Sealed"],
                scale_with_stacks=True,
                party_count_rule="DIVIDE_BY_RECIPIENTS",
                target_scope="TEAM",
            ),
        ])

    if constellation >= 2:
        buff_rules.extend([
            models.BuffRule(
                buff_id="ANASTASYA_C2_LOVE_CD",
                buff_name="C2 Love Stellar Glimmer Crit DMG",
                stat="Crit Damage",
                base_value=0.60,
                required_states=["C2 Love Buff"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C2_HONOR_MULT",
                buff_name="C2 Honor Original DMG Mult",
                stat="Original DMG Mult",
                base_value=1.25,
                required_states=["C2 Honor Buff"],
                target_scope="SELF",
                ability_filters=["Normal Attack", "Honor Burst", "Doom"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C2_HONOR_ELEV",
                buff_name="C2 Honor Stellar Glimmer Elevation",
                stat="Elevation%",
                base_value=0.05,
                required_states=["C2 Honor Buff"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
        ])

    if constellation >= 6:
        buff_rules.extend([
            models.BuffRule(
                buff_id="ANASTASYA_C6_LOVE_ELEV",
                buff_name="C6 Love Stellar Glimmer Elevation",
                stat="Elevation%",
                base_value=0.10,
                required_states=["C6 Love Elevation"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C6_HONOR_ELEV",
                buff_name="C6 Honor Stellar Glimmer Elevation",
                stat="Elevation%",
                base_value=0.20,
                required_states=["C6 Honor Elevation"],
                target_scope="SELF",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C6_FULL_ACCOLADES_CD",
                buff_name="C6 Full Party Accolades Crit DMG",
                stat="Crit Damage",
                base_value=acc_cd * 3.0,
                required_states=["Accolades", "!ANY:Sealed"],
                target_scope="SELF",
                ability_filters=["C6_DOOM_3"],
            ),
            models.BuffRule(
                buff_id="ANASTASYA_C6_FULL_ACCOLADES_ATK",
                buff_name="C6 Full Party Accolades ATK%",
                stat="ATK%",
                base_value=acc_atk * 3.0,
                required_states=["Accolades", "!ANY:Sealed"],
                target_scope="SELF",
                ability_filters=["C6_DOOM_3"],
            ),
        ])

    abilities = {
        "Skill_Tap": skill_tap,
        "Skill_Hold": skill_hold,
        "Spear_N1": spear_n1,
        "Burst_Love": burst_love,
        "Burst_Honor": burst_honor,
        "Triumph": triumph,
        "Doom": doom,
    }

    anastasya = entities.Character(
        name="Anastasya",
        element="Cryo",
        constellation=constellation,
        lvl=lvl,
        base_hp=12736.0,
        base_atk=356.0,
        base_def=779.0,
        weapon=weapon,
        weapon_type="Bow",
        artifact_set=artifact_set,
        ascension_stat={"Crit Damage": 0.384},
        artifact_stats=artifact_stats,
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={"Superconduct": "Stellar-Conduct", "Swirl": "Stellar Swirl"},
        polestar_bonus_stacks=1,
        polestar_instant_buff=True,
        instant_lv2_vortex=True,
    )

    return anastasya, abilities