import engine.entities as entities
import engine.models as models


def _radiance_variant_subs(
    parent_name: str,
    base_comp: str,
    element: str,
    attack_type: str,
    normal_mv: float,
    sc_mv: float,
    ss_mv: float,
    hit_offsets: list[float],
    extra_tags: list[str] | None = None,
    gauge_units: float = 0.0,
    icd_group: str = "NONE",
    summon_id: str | None = None,
    icd_hits: int = 3,
) -> list[models.Ability]:
    """
    Creates the 3 mutually exclusive hit variants for an attack instance that converts
    to Stellar-Conduct / Stellar Swirl DMG under Radiance: Stellar Glimmer
    (with Radiance: Stellar-Conduct taking priority over Radiance: Stellar Swirl).
    """
    base_tags = list(extra_tags) if extra_tags else []
    return [
        models.Ability(
            parent_name=parent_name,
            component_name=f"{base_comp} (Normal)",
            mv=normal_mv,
            element=element,
            attack_type=attack_type,
            tags=list(base_tags),
            hit_offsets=list(hit_offsets),
            gauge_units=gauge_units,
            icd_group=icd_group,
            summon_id=summon_id,
            required_states=["!Radiance: Stellar-Conduct", "!Radiance: Stellar Swirl"],
            icd_hits=icd_hits,
        ),
        models.Ability(
            parent_name=parent_name,
            component_name=f"{base_comp} (Stellar-Conduct)",
            mv=sc_mv,
            element=element,
            attack_type="Stellar-Conduct",
            tags=[*base_tags, "Stellar", "Stellar-Conduct"],
            hit_offsets=list(hit_offsets),
            gauge_units=gauge_units,
            icd_group=icd_group,
            summon_id=summon_id,
            required_states=["Radiance: Stellar-Conduct"],
            icd_hits=icd_hits,
        ),
        models.Ability(
            parent_name=parent_name,
            component_name=f"{base_comp} (Stellar Swirl)",
            mv=ss_mv,
            element=element,
            attack_type="Stellar Swirl",
            tags=[*base_tags, "Stellar", "Stellar Swirl"],
            hit_offsets=list(hit_offsets),
            gauge_units=gauge_units,
            icd_group=icd_group,
            summon_id=summon_id,
            required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            icd_hits=icd_hits,
        ),
    ]


def build_anastasya(
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Builds Anastasya (5-star Cryo Bow, Frostcrown Revival) at Lv. 90 with
    Talents 10 / 10 (13 at C5) / 10 (13 at C3), Passives A1/A4/P3, and C0–C6.
    """
    if weapon is None:
        weapon = entities.Weapon("DefaultBow", "Bow", 185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    skill_c5 = constellation >= 5
    burst_c3 = constellation >= 3
    skill_scale = 1.1805556 if skill_c5 else 1.0
    burst_scale = 1.1805556 if burst_c3 else 1.0

    # 1. Normal Attack: The Dawn Beyond the Everwinter (Bow, Lv. 10)
    na_1 = models.Ability(
        "The Dawn Beyond the Everwinter", "Bow 1-Hit", 0.783,
        element="Physical", attack_type="Normal Attack",
        hit_offsets=[0.20], cast_duration=0.35, gauge_units=1.0,
    )
    na_2 = models.Ability(
        "The Dawn Beyond the Everwinter", "Bow 2-Hit", 0.797,
        element="Physical", attack_type="Normal Attack",
        hit_offsets=[0.20], cast_duration=0.35, gauge_units=1.0,
    )
    na_3 = models.Ability(
        "The Dawn Beyond the Everwinter", "Bow 3-Hit", 0.499,
        element="Physical", attack_type="Normal Attack",
        hit_offsets=[0.20, 0.32], cast_duration=0.45, gauge_units=1.0,
    )
    na_4 = models.Ability(
        "The Dawn Beyond the Everwinter", "Bow 4-Hit", 0.362,
        element="Physical", attack_type="Normal Attack",
        hit_offsets=[0.20, 0.30, 0.40], cast_duration=0.55, gauge_units=1.0,
    )
    na_5 = models.Ability(
        "The Dawn Beyond the Everwinter", "Bow 5-Hit", 1.299,
        element="Physical", attack_type="Normal Attack",
        hit_offsets=[0.25], cast_duration=0.50, gauge_units=1.0,
    )
    ca_un = models.Ability(
        "The Dawn Beyond the Everwinter", "Aimed Shot", 0.867,
        element="Physical", attack_type="Charged Attack",
        hit_offsets=[0.30], cast_duration=0.50, gauge_units=1.0, icd_group="NONE",
    )
    ca_ch = models.Ability(
        "The Dawn Beyond the Everwinter", "Fully-Charged Aimed Shot", 2.232,
        element="Cryo", attack_type="Charged Attack",
        hit_offsets=[1.20], cast_duration=1.40, gauge_units=1.0, icd_group="NONE",
    )
    plunge_low = models.Ability(
        "The Dawn Beyond the Everwinter", "Low Plunge", 2.246,
        element="Physical", attack_type="Plunging Attack",
        hit_offsets=[0.50], cast_duration=0.80, gauge_units=1.0, icd_group="NONE",
    )
    plunge_high = models.Ability(
        "The Dawn Beyond the Everwinter", "High Plunge", 2.806,
        element="Physical", attack_type="Plunging Attack",
        hit_offsets=[0.60], cast_duration=0.90, gauge_units=1.0, icd_group="NONE",
    )

    # 2. Elemental Skill: Polestar's Divine Judgment (Lv. 10 / Lv. 13 at C5)
    # Tap: Gains Blessing of Love & deploys Palestar Crown (ticks every 2.0s for 20.0s = 10 ticks)
    crown_offsets = [round(2.0 * i, 1) for i in range(1, 11)]
    crown_hit_1 = models.Ability(
        "Polestar's Divine Judgment", "Palestar Crown Hit 1", 1.152 * skill_scale,
        element="Cryo", attack_type="Elemental Skill",
        tags=["Elemental Skill", "Palestar Crown"],
        hit_offsets=crown_offsets, gauge_units=1.0, icd_group="PalestarCrown",
        summon_id="Palestar Crown",
        icd_time=2,
    )
    crown_hit_2_subs = _radiance_variant_subs(
        parent_name="Polestar's Divine Judgment",
        base_comp="Palestar Crown Hit 2",
        element="Cryo",
        attack_type="Elemental Skill",
        normal_mv=1.152 * skill_scale,
        sc_mv=0.605 * skill_scale,
        ss_mv=0.907 * skill_scale,
        hit_offsets=crown_offsets,
        extra_tags=["Elemental Skill", "Palestar Crown"],
        gauge_units=0.0,
        icd_group="NONE",
        summon_id="Palestar Crown",
        icd_hits=2,
    )
    # Additional instance during To the New World (Burst_Love)
    crown_burst_extra_subs = [
        models.Ability(
            parent_name="Polestar's Divine Judgment",
            component_name="Palestar Crown Burst Extra (Stellar-Conduct)",
            mv=0.202 * burst_scale,
            element="Cryo",
            attack_type="Stellar-Conduct",
            tags=["Elemental Skill", "Palestar Crown", "Stellar", "Stellar-Conduct"],
            hit_offsets=crown_offsets,
            gauge_units=0.0,
            icd_group="NONE",
            summon_id="Palestar Crown",
            required_states=["To the New World", "!Radiance: Stellar Swirl"],
            icd_time=2,
        ),
        models.Ability(
            parent_name="Polestar's Divine Judgment",
            component_name="Palestar Crown Burst Extra (Stellar Swirl)",
            mv=0.302 * burst_scale,
            element="Cryo",
            attack_type="Stellar Swirl",
            tags=["Elemental Skill", "Palestar Crown", "Stellar", "Stellar Swirl"],
            hit_offsets=crown_offsets,
            gauge_units=0.0,
            icd_group="NONE",
            summon_id="Palestar Crown",
            required_states=["To the New World", "!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            icd_time=2,
        ),
    ]

    skill_tap = models.Ability(
        "Polestar's Divine Judgment", "Tap Skill DMG", 2.128 * skill_scale,
        element="Cryo", attack_type="Elemental Skill",
        tags=["Elemental Skill", "Anastasya Skill", "Anastasya Skill Tap"],
        hit_offsets=[0.25], cast_duration=0.45, gauge_units=1.0, icd_group="NONE",
        sub_abilities=[crown_hit_1, *crown_hit_2_subs, *crown_burst_extra_subs],
    )

    # Hold: Gains Blessing of Honor (15.0s) & enters Blessed Spear: Dolgomernoye
    skill_hold = models.Ability(
        "Polestar's Divine Judgment", "Hold Skill DMG", 2.837 * skill_scale,
        element="Cryo", attack_type="Elemental Skill",
        tags=["Elemental Skill", "Anastasya Skill", "Anastasya Skill Hold"],
        hit_offsets=[0.8], cast_duration=0.95, gauge_units=1.0, icd_group="NONE",
    )

    # Blessed Spear: Dolgomernoye Normal Attacks (Spear_N1..Spear_N5)
    # Final instance of each NA converts to Stellar-Conduct / Stellar Swirl DMG under Radiance.
    spear_n1 = models.Ability(
        "Blessed Spear: Dolgomernoye", "Spear 1-Hit", 0.0,
        element="Cryo", attack_type="Normal Attack",
        tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
        hit_offsets=[], cast_duration=0.3333 + 0.0823,
        sub_abilities=_radiance_variant_subs(
            "Blessed Spear: Dolgomernoye", "Spear 1-Hit", "Cryo", "Normal Attack",
            normal_mv=1.129 * skill_scale,
            sc_mv=0.780 * skill_scale,
            ss_mv=1.170 * skill_scale,
            hit_offsets=[0.1667],
            extra_tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
            gauge_units=1.0,
            icd_group="BlessedSpearNA",
            icd_hits=2,
        ),
    )
    spear_n2 = models.Ability(
        "Blessed Spear: Dolgomernoye", "Spear 2-Hit", 0.591 * skill_scale,
        element="Cryo", attack_type="Normal Attack",
        tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
        hit_offsets=[0.2000], cast_duration=0.65 + 0.0823, gauge_units=1.0, icd_group="BlessedSpearNA", icd_hits=2,
        sub_abilities=_radiance_variant_subs(
            "Blessed Spear: Dolgomernoye", "Spear 2-Hit Final", "Cryo", "Normal Attack",
            normal_mv=0.591 * skill_scale,
            sc_mv=0.817 * skill_scale,
            ss_mv=1.226 * skill_scale,
            hit_offsets=[0.4333],
            extra_tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
            gauge_units=1.0,
            icd_group="BlessedSpearNA",
            icd_hits=2,
        ),
    )
    spear_n3 = models.Ability(
        "Blessed Spear: Dolgomernoye", "Spear 3-Hit", 0.0,
        element="Cryo", attack_type="Normal Attack",
        tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
        hit_offsets=[], cast_duration=0.2667 + 0.0823,
        sub_abilities=_radiance_variant_subs(
            "Blessed Spear: Dolgomernoye", "Spear 3-Hit", "Cryo", "Normal Attack",
            normal_mv=1.435 * skill_scale,
            sc_mv=0.992 * skill_scale,
            ss_mv=1.488 * skill_scale,
            hit_offsets=[0.1833],
            extra_tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
            gauge_units=1.0,
            icd_group="BlessedSpearNA",
            icd_hits=2,
        ),
    )
    spear_n4 = models.Ability(
        "Blessed Spear: Dolgomernoye", "Spear 4-Hit", 0.530 * skill_scale,
        element="Cryo", attack_type="Normal Attack",
        tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
        hit_offsets=[0.18, 0.28], cast_duration=0.8333, gauge_units=1.0, icd_group="BlessedSpearNA", icd_hits=2,
        sub_abilities=_radiance_variant_subs(
            "Blessed Spear: Dolgomernoye", "Spear 4-Hit Final", "Cryo", "Normal Attack",
            normal_mv=0.530 * skill_scale,
            sc_mv=1.134 * skill_scale,
            ss_mv=1.701 * skill_scale,
            hit_offsets=[0.38],
            extra_tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
            gauge_units=1.0,
            icd_group="BlessedSpearNA",
            icd_hits=2,
        ),
    )
    spear_n5 = models.Ability(
        "Blessed Spear: Dolgomernoye", "Spear 5-Hit", 0.638 * skill_scale,
        element="Cryo", attack_type="Normal Attack",
        tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
        hit_offsets=[0.20, 0.32], cast_duration=0.8333, gauge_units=1.0, icd_group="BlessedSpearNA", icd_hits=2,
        sub_abilities=_radiance_variant_subs(
            "Blessed Spear: Dolgomernoye", "Spear 5-Hit Final", "Cryo", "Normal Attack",
            normal_mv=0.638 * skill_scale,
            sc_mv=1.384 * skill_scale,
            ss_mv=2.076 * skill_scale,
            hit_offsets=[0.44],
            extra_tags=["Normal Attack", "Blessed Spear", "Blessed Spear: Dolgomernoye"],
            gauge_units=1.0,
            icd_group="BlessedSpearNA",
            icd_hits=2,
        ),
    )

    # 3. Elemental Burst: To the New World / The Evernight Yields to Dawn (Lv. 10 / Lv. 13 at C3)
    burst_love = models.Ability(
        "To the New World", "To the New World Skill DMG", 3.607 * burst_scale,
        element="Cryo", attack_type="Elemental Burst",
        tags=["Elemental Burst", "To the New World"],
        hit_offsets=[0.80], cast_duration=1.50, gauge_units=2.0, icd_group="NONE",
        required_states=["!Blessing of Honor"],
    )

    burst_honor = models.Ability(
        "The Evernight Yields to Dawn", "The Evernight Yields to Dawn", 0.0,
        element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Burst", "Evernight Yields to Dawn", "The Evernight Yields to Dawn"],
        hit_offsets=[], cast_duration=1.8333,
        required_states=["Blessing of Honor"],
        sub_abilities=[
            models.Ability(
                "The Evernight Yields to Dawn", "Evernight Burst (Stellar-Conduct)",
                5.611 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Burst", "Evernight Yields to Dawn", "Stellar", "Stellar-Conduct"],
                hit_offsets=[1.8333], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "The Evernight Yields to Dawn", "Evernight Burst (Stellar Swirl)",
                8.417 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Burst", "Evernight Yields to Dawn", "Stellar", "Stellar Swirl"],
                hit_offsets=[1.8333], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )

    # Special Unsealing Elemental Skills: Palestar Edict: Triumph & Palestar Edict: Doom
    triumph = models.Ability(
        "Palestar Edict: Triumph", "Palestar Edict: Triumph", 0.0,
        element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Palestar Edict: Triumph"],
        hit_offsets=[], cast_duration=0.40,
        sub_abilities=[
            models.Ability(
                "Palestar Edict: Triumph", "Triumph (Stellar-Conduct)",
                4.008 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Triumph", "Stellar", "Stellar-Conduct"],
                hit_offsets=[0.20], gauge_units=1.0,
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Triumph", "Triumph (Stellar Swirl)",
                6.012 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Triumph", "Stellar", "Stellar Swirl"],
                hit_offsets=[0.20], gauge_units=1.0,
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )

    doom_1 = models.Ability(
        "Palestar Edict: Doom", "Doom Stage 1", 0.481 * burst_scale,
        element="Cryo", attack_type="Elemental Skill",
        tags=["Elemental Skill", "Palestar Edict: Doom"],
        hit_offsets=[0.10, 0.18, 0.26, 0.34, 0.42], cast_duration=0.70,
        gauge_units=1.0, icd_group="PalestarDoom", icd_time=2.5, icd_hits=3,
        sub_abilities=[
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 1 (Stellar-Conduct)",
                1.202 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
                hit_offsets=[0.5667], gauge_units=0.0,
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 1 (Stellar Swirl)",
                1.804 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
                hit_offsets=[0.5667], gauge_units=0.0,
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )
    doom_2 = models.Ability(
        "Palestar Edict: Doom", "Doom Stage 2", 0.0,
        element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Palestar Edict: Doom"],
        hit_offsets=[], cast_duration=0.80,
        sub_abilities=[
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 2 (Stellar-Conduct)",
                2.004 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
                hit_offsets=[0.4167], gauge_units=0.0,
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 2 (Stellar Swirl)",
                3.006 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
                hit_offsets=[0.4167], gauge_units=0.0,
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )
    doom_3 = models.Ability(
        "Palestar Edict: Doom", "Doom Stage 3", 0.0,
        element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Palestar Edict: Doom"],
        hit_offsets=[], cast_duration=1.7333,
        sub_abilities=[
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 3 (Stellar-Conduct)",
                2.806 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
                hit_offsets=[1.2833], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 3 (Stellar Swirl)",
                4.208 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
                hit_offsets=[1.2833], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )
    doom_full = models.Ability(
        "Palestar Edict: Doom", "Palestar Edict: Doom (Full)", 0.481 * burst_scale,
        element="Cryo", attack_type="Elemental Skill",
        tags=["Elemental Skill", "Palestar Edict: Doom"],
        hit_offsets=[0.10, 0.18, 0.26, 0.34, 0.42], cast_duration=3,
        gauge_units=1.0, icd_group="PalestarDoom",
        sub_abilities=[
            *doom_1.sub_abilities,
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 2 Full (Stellar-Conduct)",
                2.004 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
                hit_offsets=[1.3333], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 2 Full (Stellar Swirl)",
                3.006 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
                hit_offsets=[1.3333], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 3 Full (Stellar-Conduct)",
                2.806 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
                hit_offsets=[3.00], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar Swirl"],
            ),
            models.Ability(
                "Palestar Edict: Doom", "Doom Stage 3 Full (Stellar Swirl)",
                4.208 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
                tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
                hit_offsets=[3.00], gauge_units=1.0, icd_group="NONE",
                required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
            ),
        ],
    )

    # C6 Special Coordinated Attacks (200% Triumph on Love swap-in; 250% Doom 3 on Honor tap Skill)
    c6_triumph_sc = models.Ability(
        "Look Up, a Dawn Unstained Shall Rise", "C6 Triumph (Stellar-Conduct)",
        2.0 * 4.008 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Palestar Edict: Triumph", "Stellar", "Stellar-Conduct"],
        hit_offsets=[0.0], gauge_units=1.0, icd_group="NONE",
        required_states=["!Radiance: Stellar Swirl"],
    )
    c6_triumph_ss = models.Ability(
        "Look Up, a Dawn Unstained Shall Rise", "C6 Triumph (Stellar Swirl)",
        2.0 * 6.012 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
        tags=["Elemental Skill", "Palestar Edict: Triumph", "Stellar", "Stellar Swirl"],
        hit_offsets=[0.0], gauge_units=1.0, icd_group="NONE",
        required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
    )
    c6_doom3_sc = models.Ability(
        "Look Up, a Dawn Unstained Shall Rise", "C6 Doom Stage 3 (Stellar-Conduct)",
        2.5 * 2.806 * burst_scale, element="Cryo", attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar-Conduct"],
        cast_duration=1.7333,
        hit_offsets=[1.2833], gauge_units=1.0, icd_group="NONE",
        required_states=["!Radiance: Stellar Swirl"],
    )
    c6_doom3_ss = models.Ability(
        "Look Up, a Dawn Unstained Shall Rise", "C6 Doom Stage 3 (Stellar Swirl)",
        2.5 * 4.208 * burst_scale, element="Cryo", attack_type="Stellar Swirl",
        tags=["Elemental Skill", "Palestar Edict: Doom", "Stellar", "Stellar Swirl"],
        hit_offsets=[0.0], gauge_units=1.0, icd_group="NONE",
        required_states=["!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
    )

    # 4. State Rules (Blessings, Bursts, Sealing, A1 Accolades, P3 Radiance, C2, C6)
    state_rules = [
        # Tap Skill: Gain Blessing of Love (clears Blessing of Honor) & grant A1 Accolades (20s)
        models.StateRule(
            state_id="Blessing of Love",
            base_duration=float("inf"),
            trigger_tags=["CAST", "Anastasya Skill Tap"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            termination_rules=["Blessing of Honor"],
            target_scope="SELF",
        ),
        # Hold Skill: Gain Blessing of Honor (15.0s, clears Blessing of Love)
        models.StateRule(
            state_id="Blessing of Honor",
            base_duration=15.0,
            trigger_tags=["CAST", "Anastasya Skill Hold"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            termination_rules=["Blessing of Love"],
            target_scope="SELF",
        ),
        # Burst (Love): To the New World (20.0s) & freezes Palestar Crown duration
        models.StateRule(
            state_id="To the New World",
            base_duration=20.0,
            trigger_tags=["CAST", "To the New World"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            freeze_state=["Palestar Crown"],
            target_scope="GLOBAL",
        ),
        # Burst (Love) Sealing: Switching Anastasya off-field during To the New World Seals her
        models.StateRule(
            state_id="Anastasya Sealed",
            base_duration=20.0,
            trigger_tags=["SWAP_OUT"],
            trigger_scope="SELF",
            required_states=["To the New World"],
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
        # When Anastasya's Sealed state ends, she can trigger Palestar Edict: Triumph on swap-in
        models.StateRule(
            state_id="Triumph Ready",
            base_duration=8.0,
            trigger_tags=["STATE_EXPIRE", "Anastasya Sealed"],
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Triumph Swap Trigger",
            base_duration=0.0,
            trigger_tags=["SWAP_IN"],
            trigger_scope="SELF",
            required_states=["Triumph Ready"],
            consume_stacks={"Triumph Ready": 1},
            target_scope="SELF",
            triggered_ability=triumph,
        ),
        # Burst (Honor): The Evernight Yields to Dawn (14.0s), freezes Blessing of Honor & Seals teammates
        models.StateRule(
            state_id="Evernight Yields to Dawn",
            base_duration=14.0,
            trigger_tags=["CAST", "Evernight Yields to Dawn"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            freeze_state=["Blessing of Honor"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Teammates Sealed",
            base_duration=14.0,
            trigger_tags=["CAST", "Evernight Yields to Dawn"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
        models.StateRule(
            state_id="Doom Ready",
            base_duration=8.0,
            trigger_tags=["STATE_EXPIRE", "Teammates Sealed"],
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        # A1: All party members gain Accolades for 20s after Anastasya uses Elemental Skill
        models.StateRule(
            state_id="Accolades",
            base_duration=20.0,
            trigger_tags=["CAST", "Anastasya Skill"],
            trigger_scope="SELF",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="GLOBAL",
        ),
        # P3: Anastasya gains Radiance: Stellar Swirl for 8s when any party member triggers Stellar Swirl
        models.StateRule(
            state_id="Radiance: Stellar Swirl",
            base_duration=8.0,
            trigger_tags=["REACTION", "Stellar Swirl"],
            trigger_scope="TEAM",
            max_stacks=1,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
    ]

    if constellation >= 2:
        state_rules.extend([
            # C2 (Love): +50% Stellar Glimmer Crit DMG for 30s on Tap Skill
            models.StateRule(
                state_id="Anastasya C2 Love",
                base_duration=30.0,
                trigger_tags=["CAST", "Anastasya Skill Tap"],
                trigger_scope="SELF",
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            ),
            # C2 (Honor): 125% Original DMG for NA, Evernight Burst, and Doom for 15s on Hold Skill
            models.StateRule(
                state_id="Anastasya C2 Honor",
                base_duration=15.0,
                trigger_tags=["CAST", "Anastasya Skill Hold"],
                trigger_scope="SELF",
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="SELF",
            ),
        ])

    if constellation >= 6:
        state_rules.extend([
            # C6 (Love): Armed on Tap Skill (30s, 15s CD) -> next teammate swap-in triggers 200% Triumph
            models.StateRule(
                state_id="Anastasya C6 Love Armed",
                base_duration=30.0,
                trigger_tags=["CAST", "Anastasya Skill Tap"],
                trigger_scope="SELF",
                trigger_icd=15.0,
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
            ),
            models.StateRule(
                state_id="Anastasya C6 Love Fire",
                base_duration=0.0,
                trigger_tags=["SWAP_IN"],
                trigger_scope="OTHER_TEAMMATES",
                required_states=["Anastasya C6 Love Armed"],
                consume_stacks={"Anastasya C6 Love Armed": 1},
                target_scope="GLOBAL",
                triggered_ability=c6_triumph_sc,
            ),
            models.StateRule(
                state_id="Anastasya C6 Love Fire SS",
                base_duration=0.0,
                trigger_tags=["SWAP_IN"],
                trigger_scope="OTHER_TEAMMATES",
                required_states=["Anastasya C6 Love Armed", "!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
                consume_stacks={"Anastasya C6 Love Armed": 1},
                target_scope="GLOBAL",
                triggered_ability=c6_triumph_ss,
            ),
            # C6 (Honor): Armed on Hold Skill (30s, 15s CD) -> next Tap Skill triggers 250% Doom 3
            models.StateRule(
                state_id="Anastasya C6 Honor Armed",
                base_duration=30.0,
                trigger_tags=["CAST", "Anastasya Skill Hold"],
                trigger_scope="SELF",
                trigger_icd=15.0,
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="SELF",
            ),
            models.StateRule(
                state_id="Anastasya C6 Honor Fire",
                base_duration=0.0,
                trigger_tags=["CAST", "Anastasya Skill Tap"],
                trigger_scope="SELF",
                required_states=["Anastasya C6 Honor Armed"],
                consume_stacks={"Anastasya C6 Honor Armed": 1},
                target_scope="SELF",
                triggered_ability=c6_doom3_sc,
            ),
            models.StateRule(
                state_id="Anastasya C6 Honor Fire SS",
                base_duration=0.0,
                trigger_tags=["CAST", "Anastasya Skill Tap"],
                trigger_scope="SELF",
                required_states=["Anastasya C6 Honor Armed", "!Radiance: Stellar-Conduct", "Radiance: Stellar Swirl"],
                consume_stacks={"Anastasya C6 Honor Armed": 1},
                target_scope="SELF",
                triggered_ability=c6_doom3_ss,
            ),
        ])

    # 5. Buff Rules (A1 Accolades + Sealing Division, A4, P3, Burst_Love, C1, C2, C4, C6)
    accolade_mult = 1.30 if constellation >= 4 else 1.0
    base_cd = 0.12 * accolade_mult
    base_cryo_atk = 0.15 * accolade_mult
    base_other_em = 60.0 * accolade_mult

    # Sealing division multipliers:
    # - Normal (neither Sealed): 1.0x for all
    # - Anastasya Sealed (Love): Anastasya gets 0x at C0 (1.0x at C1+); teammates get 1 + 1/3 = 4/3x at C0 (1 + 1.0 = 2.0x at C1+)
    # - Teammates Sealed (Honor): Anastasya gets 1 + 3 = 4.0x; teammates get 0x at C0 (1.0x at C1+)
    ana_sealed_self_mult = 1.0 if constellation >= 1 else 0.0
    ana_sealed_tm_mult = 2.0 if constellation >= 1 else (4.0 / 3.0)
    tm_sealed_tm_mult = 1.0 if constellation >= 1 else 0.0

    buff_rules = [
        # A1 Accolades: Unsealed baseline (+12% CD / +15.6% at C4)
        models.BuffRule(
            buff_id="ANA_A1_ACCOLADES_CD_NORMAL",
            buff_name="Accolades Crit DMG",
            stat="Crit Damage",
            base_value=base_cd,
            required_states=["Accolades", "!Anastasya Sealed", "!Teammates Sealed"],
            target_scope="TEAM",
        ),
        # A1 Accolades when Anastasya is Sealed (Love): teammates get divided share (+16% at C0, +24% at C1, +31.2% at C4)
        models.BuffRule(
            buff_id="ANA_A1_ACCOLADES_CD_ANA_SEALED_TM",
            buff_name="Accolades Crit DMG (Anastasya Sealed Share)",
            stat="Crit Damage",
            base_value=base_cd * ana_sealed_tm_mult,
            required_states=["Accolades", "Anastasya Sealed"],
            target_scope="OTHER_TEAMMATES",
        ),
        # A1 Accolades when Teammates are Sealed (Honor): Anastasya absorbs all 3 teammates' shares (4x = +48% / +62.4% at C4)
        models.BuffRule(
            buff_id="ANA_A1_ACCOLADES_CD_TM_SEALED_SELF",
            buff_name="Accolades Crit DMG (Teammates Sealed Share)",
            stat="Crit Damage",
            base_value=base_cd * 4.0,
            required_states=["Accolades", "Teammates Sealed"],
            target_scope="SELF",
        ),
        # Burst (Love): To the New World grants +30.0% (Lv. 10) / +35.4% (Lv. 13 C3) Stellar Glimmer Reaction DMG%
        models.BuffRule(
            buff_id="ANA_BURST_LOVE_SG_DMG",
            buff_name="To the New World Stellar Glimmer DMG%",
            stat="Reaction DMG%",
            base_value=0.30 * burst_scale,
            required_states=["To the New World"],
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
        # A4: Stellar Swirl base reaction multiplier +10%
        models.BuffRule(
            buff_id="ANA_A4_STELLAR_SWIRL_BASE",
            buff_name="Lament for the Lost Stellar Swirl Base Mult",
            stat="Base Reaction Coefficient",
            base_value=0.10,
            target_scope="TEAM",
            ability_filters=["Stellar Swirl"],
        ),
        # P3: +0.7% Stellar-Conduct & Stellar Swirl base DMG per 100 ATK (0.00007 per 1 ATK), up to 14%
        models.BuffRule(
            buff_id="ANA_P3_ATK_TO_SG_BASE",
            buff_name="Stellar Jubilee Base Reaction Bonus",
            stat="Reaction Base DMG%",
            base_value=0.00007,
            scaling_stat="ATK",
            max_value=0.14,
            scaling_order=3,
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct", "Stellar Swirl"],
        ),
    ]

    if constellation >= 1:
        buff_rules.extend([
            # C1: Anastasya retains her Accolades while Sealed
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CD_SELF_RETAINED",
                buff_name="Accolades Crit DMG (C1 Retained)",
                stat="Crit Damage",
                base_value=base_cd * ana_sealed_self_mult,
                required_states=["Accolades", "Anastasya Sealed"],
                target_scope="SELF",
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CD_TM_RETAINED",
                buff_name="Accolades Crit DMG (C1 Teammates Retained)",
                stat="Crit Damage",
                base_value=base_cd * tm_sealed_tm_mult,
                required_states=["Accolades", "Teammates Sealed"],
                target_scope="OTHER_TEAMMATES",
            ),
            # C1: Accolades grants +15% ATK (+19.5% at C4) to Cryo characters
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CRYO_ATK_NORMAL",
                buff_name="Accolades Cryo ATK%",
                stat="ATK%",
                base_value=base_cryo_atk,
                required_states=["Accolades", "!Anastasya Sealed", "!Teammates Sealed"],
                target_scope="TEAM",
                char_element_filters=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CRYO_ATK_ANA_SEALED_SELF",
                buff_name="Accolades Cryo ATK% (Anastasya Sealed Retained)",
                stat="ATK%",
                base_value=base_cryo_atk,
                required_states=["Accolades", "Anastasya Sealed"],
                target_scope="SELF",
                char_element_filters=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CRYO_ATK_ANA_SEALED_TM",
                buff_name="Accolades Cryo ATK% (Anastasya Sealed 300% Share)",
                stat="ATK%",
                base_value=base_cryo_atk * ana_sealed_tm_mult,
                required_states=["Accolades", "Anastasya Sealed"],
                target_scope="OTHER_TEAMMATES",
                char_element_filters=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CRYO_ATK_TM_SEALED_SELF",
                buff_name="Accolades Cryo ATK% (Teammates Sealed 4x)",
                stat="ATK%",
                base_value=base_cryo_atk * 4.0,
                required_states=["Accolades", "Teammates Sealed"],
                target_scope="SELF",
                char_element_filters=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_CRYO_ATK_TM_SEALED_TM",
                buff_name="Accolades Cryo ATK% (Teammates Sealed Retained)",
                stat="ATK%",
                base_value=base_cryo_atk,
                required_states=["Accolades", "Teammates Sealed"],
                target_scope="OTHER_TEAMMATES",
                char_element_filters=["Cryo"],
            ),
            # C1: Accolades grants +60 EM (+78 EM at C4) to non-Cryo characters
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_OTHER_EM_NORMAL",
                buff_name="Accolades Non-Cryo EM",
                stat="Elemental Mastery",
                base_value=base_other_em,
                required_states=["Accolades", "!Anastasya Sealed", "!Teammates Sealed"],
                target_scope="TEAM",
                exclude_char_elements=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_OTHER_EM_ANA_SEALED_TM",
                buff_name="Accolades Non-Cryo EM (Anastasya Sealed 300% Share)",
                stat="Elemental Mastery",
                base_value=base_other_em * ana_sealed_tm_mult,
                required_states=["Accolades", "Anastasya Sealed"],
                target_scope="OTHER_TEAMMATES",
                exclude_char_elements=["Cryo"],
            ),
            models.BuffRule(
                buff_id="ANA_C1_ACCOLADES_OTHER_EM_TM_SEALED_TM",
                buff_name="Accolades Non-Cryo EM (Teammates Sealed Retained)",
                stat="Elemental Mastery",
                base_value=base_other_em,
                required_states=["Accolades", "Teammates Sealed"],
                target_scope="OTHER_TEAMMATES",
                exclude_char_elements=["Cryo"],
            ),
        ])

    if constellation >= 2:
        buff_rules.extend([
            # C2: Party Stellar Glimmer Reaction DMG is Elevated by 5%
            models.BuffRule(
                buff_id="ANA_C2_SG_ELEVATION",
                buff_name="To Winter C2 Stellar Glimmer Elevation",
                stat="Elevation",
                base_value=0.05,
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            # C2 (Love): +50% Crit DMG for party Stellar Glimmer Reaction DMG
            models.BuffRule(
                buff_id="ANA_C2_LOVE_SG_CD",
                buff_name="To Winter C2 Love Stellar Glimmer Crit DMG",
                stat="Crit Damage",
                base_value=0.50,
                required_states=["Anastasya C2 Love"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            # C2 (Honor): Anastasya's NAs, Evernight Burst, and Doom deal 125% Original DMG
            models.BuffRule(
                buff_id="ANA_C2_HONOR_ORIG_DMG",
                buff_name="To Winter C2 Honor 125% Original DMG",
                stat="Original DMG Mult",
                base_value=1.25,
                required_states=["Anastasya C2 Honor"],
                target_scope="SELF",
                ability_filters=[
                    "The Dawn Beyond the Everwinter",
                    "Blessed Spear",
                    "Blessed Spear: Dolgomernoye",
                    "The Evernight Yields to Dawn",
                    "Palestar Edict: Doom",
                ],
            ),
        ])

    if constellation >= 6:
        buff_rules.extend([
            # C6 (Love): Party Stellar Glimmer Reaction DMG Elevated by 10% for 30s
            models.BuffRule(
                buff_id="ANA_C6_LOVE_SG_ELEVATION",
                buff_name="Look Up C6 Love Party Stellar Glimmer Elevation",
                stat="Elevation",
                base_value=0.10,
                required_states=["Anastasya C6 Love Armed"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
            # C6 (Honor): Anastasya's Stellar Glimmer Reaction DMG Elevated by 20% for 30s
            models.BuffRule(
                buff_id="ANA_C6_HONOR_SG_ELEVATION",
                buff_name="Look Up C6 Honor Self Stellar Glimmer Elevation",
                stat="Elevation",
                base_value=0.20,
                required_states=["Anastasya C6 Honor Armed"],
                target_scope="SELF",
                ability_filters=["Stellar-Conduct", "Stellar Swirl"],
            ),
        ])

    # 6. Character Assembly & Ability Dictionary
    character = entities.Character(
        name="Anastasya",
        element="Cryo",
        constellation=constellation,
        base_hp=12736.0,
        base_atk=356.0,
        base_def=779.0,
        weapon=weapon,
        weapon_type="Bow",
        artifact_set=artifact_set,
        artifact_stats=artifact_stats,
        ascension_stat={"Crit Damage": 0.384},
        lvl=lvl,
        reaction_override={
            "Superconduct": "Stellar-Conduct",
            "Swirl": "Stellar Swirl",
        },
        polestar_bonus_stacks=1,
        polestar_instant_buff=True,
        instant_lv2_vortex=True,
        state_rules=state_rules,
        buff_rules=buff_rules,
    )

    abilities = {
        "N1": na_1,
        "N2": na_2,
        "N3": na_3,
        "N4": na_4,
        "N5": na_5,
        "CA": ca_un,
        "CA_Charged": ca_ch,
        "Plunge_Low": plunge_low,
        "Plunge_High": plunge_high,
        "Skill_Tap": skill_tap,
        "Skill_Hold": skill_hold,
        "Spear_N1": spear_n1,
        "Spear_N2": spear_n2,
        "Spear_N3": spear_n3,
        "Spear_N4": spear_n4,
        "Spear_N5": spear_n5,
        "Burst_Love": burst_love,
        "Burst_Honor": burst_honor,
        "Triumph": triumph,
        "Doom_1": doom_1,
        "Doom_2": doom_2,
        "Doom_3": doom_3,
        "Doom": doom_full,
        "Doom_C6": c6_doom3_sc,
    }

    return character, abilities