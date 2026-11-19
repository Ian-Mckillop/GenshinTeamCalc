import engine.entities as entities
import engine.models as models


def build_danica(
    constellation: int = 0,
    weapon: entities.Weapon | None = None,
    artifact_set: list[entities.ArtifactSet] | None = None,
    artifact_stats: dict[str, float] | None = None,
    lvl: int = 90,
) -> tuple[entities.Character, dict[str, models.Ability]]:
    """
    Builds Danica (5-star Electro Sword) with full C0-C6 kit, passives, and ability dictionary.
    Note: Base HP/ATK/DEF and Crit Rate ascension use standard 5-star Electro Sword defaults
    since the stat page was not included in the kit screenshots.
    """
    if weapon is None:
        weapon = entities.Weapon(name="Waster Greatsword", type="Claymore", base_atk=185.0)
    if artifact_set is None:
        artifact_set = []
    if artifact_stats is None:
        artifact_stats = {}

    skill_c5 = constellation >= 5
    burst_c3 = constellation >= 3

    # --- Talent Multipliers (Lv. 10 vs Lv. 13 for C3/C5) ---
    skill_mv = 0.908 if skill_c5 else 0.770
    protect_mv = 1.442 if skill_c5 else 1.221
    purge_mv = 1.696 if skill_c5 else 1.437
    coord_mv = 0.809 if skill_c5 else 0.685
    sa_na1_mv = 1.566 if skill_c5 else 1.326
    sa_na2_mv = 1.432 if skill_c5 else 1.213
    sa_na3_mv = 0.934 if skill_c5 else 0.791
    sa_na4_mv = 2.289 if skill_c5 else 1.939

    burst_h1_mv = 1.589 if burst_c3 else 1.346
    burst_h1_sc_mv = 0.940 if burst_c3 else 0.796
    burst_mid_mv = 0.251 if burst_c3 else 0.213
    burst_h5_mv = 1.840 if burst_c3 else 1.559
    burst_h5_sc_mv = 1.409 if burst_c3 else 1.193

    burst_rg_ratio = 0.118 if burst_c3 else 0.100
    burst_rg_cap = 472.0 if burst_c3 else 400.0
    burst_cleaner_purge_dmg = 0.830 if burst_c3 else 0.703

    if constellation >= 1:
        burst_rg_ratio *= 1.80
        burst_rg_cap *= 1.80
        burst_cleaner_purge_dmg *= 2.20

    # --- Normal / Charged / Plunge Attacks (Canon of Cleanliness) ---
    n1 = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Normal 1-Hit",
        mv=1.255,
        element="Physical",
        attack_type="Normal Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.35,
        hit_offsets=[0.15],
        is_blunt=True,
    )
    n2 = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Normal 2-Hit",
        mv=1.148,
        element="Physical",
        attack_type="Normal Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.35,
        hit_offsets=[0.15],
        is_blunt=True,
    )
    n3 = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Normal 3-Hit",
        mv=0.749,
        total_hits=2,
        element="Physical",
        attack_type="Normal Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.45,
        hit_offsets=[0.15, 0.28],
        is_blunt=True,
    )
    n4 = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Normal 4-Hit",
        mv=1.835,
        element="Physical",
        attack_type="Normal Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.55,
        hit_offsets=[0.25],
        is_blunt=True,
    )
    ca_cyclic = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Charged Attack Cyclic",
        mv=1.236,
        element="Physical",
        attack_type="Charged Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.40,
        hit_offsets=[0.20],
        is_blunt=True,
    )
    ca_final = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Charged Attack Final",
        mv=2.240,
        element="Physical",
        attack_type="Charged Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.50,
        hit_offsets=[0.25],
        is_blunt=True,
    )
    plunge_low = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="Low Plunge",
        mv=2.950,
        element="Physical",
        attack_type="Plunging Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.60,
        hit_offsets=[0.30],
        is_blunt=True,
    )
    plunge_high = models.Ability(
        parent_name="Canon of Cleanliness",
        component_name="High Plunge",
        mv=3.680,
        element="Physical",
        attack_type="Plunging Attack",
        required_states=["!Storm Anchor"],
        cast_duration=0.60,
        hit_offsets=[0.30],
        is_blunt=True,
    )

    # --- Storm Anchor Infused Normal Attacks ---
    sa_n1 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 1-Hit",
        mv=sa_na1_mv,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        tags=["SA_NA_Hit"],
        cast_duration=0.35,
        hit_offsets=[0.15],
        is_blunt=True,
    )
    sa_n2 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 2-Hit",
        mv=sa_na2_mv,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        tags=["SA_NA_Hit"],
        cast_duration=0.35,
        hit_offsets=[0.15],
        is_blunt=True,
    )
    sa_n3_h1 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 3-Hit",
        mv=sa_na3_mv,
        hit_index=1,
        total_hits=2,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        tags=["SA_NA_Hit"],
        cast_duration=0.45,
        hit_offsets=[0.15],
        is_blunt=True,
    )
    sa_n3_h2 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 3-Hit",
        mv=sa_na3_mv,
        hit_index=2,
        total_hits=2,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        hit_offsets=[0.28],
        is_blunt=True,
    )
    sa_n3 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 3-Hit",
        mv=0.0,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        cast_duration=0.45,
        sub_abilities=[sa_n3_h1, sa_n3_h2],
        is_blunt=True,
    )
    sa_n4 = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Normal 4-Hit",
        mv=sa_na4_mv,
        element="Electro",
        attack_type="Normal Attack",
        required_states=["Storm Anchor"],
        tags=["SA_NA_Hit"],
        cast_duration=0.55,
        hit_offsets=[0.25],
        is_blunt=True,
    )

    # --- Elemental Skill & Special Skills ---
    skill = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Skill DMG",
        mv=skill_mv,
        element="Electro",
        attack_type="Elemental Skill",
        tags=["Scouring Anchor"],
        cast_duration=0.50,
        hit_offsets=[0.25],
    )

    coordinated_atk = models.Ability(
        parent_name="Scouring Anchor",
        component_name="Storm Anchor Coordinated Attack",
        mv=coord_mv,
        element="Electro",
        attack_type="Elemental Skill",
        icd_group="STORM_ANCHOR_COORD",
        hit_offsets=[0.05],
    )

    will_to_protect_hit = models.Ability(
        parent_name="Will to Protect",
        component_name="Will to Protect DMG",
        mv=protect_mv,
        element="Electro",
        attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Will to Protect"],
        icd_group="NONE",
        hit_offsets=[0.05],
    )
    will_to_protect_cast = models.Ability(
        parent_name="Will to Protect",
        component_name="Will to Protect Cast",
        mv=0.0,
        element="Electro",
        attack_type="Elemental Skill",
        tags=["Will to Protect"],
        cast_duration=0.30,
        hit_offsets=[],
    )

    will_to_purge_hit = models.Ability(
        parent_name="Will to Purge",
        component_name="Will to Purge DMG",
        mv=purge_mv,
        element="Electro",
        attack_type="Stellar-Conduct",
        tags=["Elemental Skill", "Stellar", "Stellar-Conduct", "Will to Purge"],
        icd_group="NONE",
        hit_offsets=[0.15],
    )
    will_to_purge_cast = models.Ability(
        parent_name="Will to Purge",
        component_name="Will to Purge Cast",
        mv=0.0,
        element="Electro",
        attack_type="Elemental Skill",
        tags=["Will to Purge"],
        cast_duration=0.40,
        hit_offsets=[],
    )

    # --- Elemental Burst (Rite to Cleanse the World) ---
    burst_h1 = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 1-Hit",
        mv=burst_h1_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.20],
    )
    burst_h1_sc = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 1-Hit Stellar-Conduct",
        mv=burst_h1_sc_mv,
        element="Electro",
        attack_type="Stellar-Conduct",
        required_states=["Radiance: Stellar-Conduct"],
        tags=["Elemental Burst", "Stellar", "Stellar-Conduct"],
        icd_group="NONE",
        hit_offsets=[0.20],
    )
    burst_h2 = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 2-Hit",
        mv=burst_mid_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.40],
    )
    burst_h3 = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 3-Hit",
        mv=burst_mid_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.60],
    )
    burst_h4 = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 4-Hit",
        mv=burst_mid_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[0.80],
    )
    burst_h5 = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 5-Hit",
        mv=burst_h5_mv,
        element="Electro",
        attack_type="Elemental Burst",
        hit_offsets=[1.00],
    )
    burst_h5_sc = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Burst 5-Hit Stellar-Conduct",
        mv=burst_h5_sc_mv,
        element="Electro",
        attack_type="Stellar-Conduct",
        required_states=["Radiance: Stellar-Conduct"],
        tags=["Elemental Burst", "Stellar", "Stellar-Conduct"],
        icd_group="NONE",
        hit_offsets=[1.00],
    )
    burst = models.Ability(
        parent_name="Rite to Cleanse the World",
        component_name="Rite to Cleanse the World",
        mv=0.0,
        element="Electro",
        attack_type="Elemental Burst",
        tags=["Rite to Cleanse the World"],
        cast_duration=1.20,
        sub_abilities=[burst_h1, burst_h1_sc, burst_h2, burst_h3, burst_h4, burst_h5, burst_h5_sc],
    )

    # --- State Rules ---
    state_rules = [
        # Summon Storm Anchor (25.0s)
        models.StateRule(
            state_id="Storm Anchor",
            base_duration=25.0,
            trigger_tags=["CAST", "Scouring Anchor"],
            target_scope="GLOBAL",
        ),
        models.StateRule(
            state_id="Storm Anchor Cleanup",
            base_duration=0.0,
            trigger_tags=["STATE_EXPIRE", "Storm Anchor"],
            termination_rules=["Will to Cleanse"],
            target_scope="SELF",
        ),
        # Off-field Storm Anchor Coordinated Attack (1.5s ICD on teammate Electro/Cryo HIT)
        models.StateRule(
            state_id="Storm Anchor Coord Trigger",
            base_duration=0.0,
            trigger_tags=["HIT", "Electro"],
            required_states=["Storm Anchor"],
            trigger_icd=1.5,
            trigger_scope="OTHER_TEAMMATES",
            target_scope="SELF",
            triggered_ability=coordinated_atk,
        ),
        models.StateRule(
            state_id="Storm Anchor Coord Trigger",
            base_duration=0.0,
            trigger_tags=["HIT", "Cryo"],
            required_states=["Storm Anchor"],
            trigger_icd=1.5,
            trigger_scope="OTHER_TEAMMATES",
            target_scope="SELF",
            triggered_ability=coordinated_atk,
        ),
        # Off-field Will to Cleanse gain (+50 per active teammate Electro/Cryo hit, 0.1s ICD; disabled in Cleaner form)
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "Electro"],
            required_states=["Storm Anchor", "!Maid: Cleaner"],
            stacks=50,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_icd=0.1,
            trigger_scope="OTHER_TEAMMATES",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "Cryo"],
            required_states=["Storm Anchor", "!Maid: Cleaner"],
            stacks=50,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_icd=0.1,
            trigger_scope="OTHER_TEAMMATES",
            target_scope="SELF",
        ),
        # On-field Will to Cleanse gain (+25 per Storm Anchor NA attack; disabled in Royal Guard form)
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "SA_NA_Hit"],
            required_states=["Storm Anchor", "!Maid: Royal Guard"],
            stacks=25,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_scope="SELF",
            target_scope="SELF",
        ),
        # A4 bonus Will to Cleanse (+25 per stack of A4 Cleaner Stack, up to 3 stacks)
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "SA_NA_Hit"],
            required_states=["Storm Anchor", "Maid: Cleaner", "A4 Cleaner Stack:1"],
            stacks=25,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_scope="SELF",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "SA_NA_Hit"],
            required_states=["Storm Anchor", "Maid: Cleaner", "A4 Cleaner Stack:2"],
            stacks=25,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_scope="SELF",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "SA_NA_Hit"],
            required_states=["Storm Anchor", "Maid: Cleaner", "A4 Cleaner Stack:3"],
            stacks=25,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            trigger_scope="SELF",
            target_scope="SELF",
        ),
        # Will to Protect (triggers on SWAP_IN or explicit CAST when Will to Cleanse == 100)
        models.StateRule(
            state_id="Maid: Royal Guard",
            base_duration=float("inf"),
            trigger_tags=["SWAP_IN"],
            required_states=["Storm Anchor", "Will to Cleanse:100"],
            termination_rules=[
                "Will to Cleanse",
                "Maid: Cleaner",
                "A4 Cleaner Stack",
                "Cleaner Purge Count",
                "Burst Cleaner Enhancement",
            ],
            target_scope="SELF",
            triggered_ability=will_to_protect_hit,
        ),
        models.StateRule(
            state_id="Maid: Royal Guard",
            base_duration=float("inf"),
            trigger_tags=["CAST", "Will to Protect"],
            required_states=["Storm Anchor", "Will to Cleanse:100"],
            termination_rules=[
                "Will to Cleanse",
                "Maid: Cleaner",
                "A4 Cleaner Stack",
                "Cleaner Purge Count",
                "Burst Cleaner Enhancement",
            ],
            target_scope="SELF",
            triggered_ability=will_to_protect_hit,
        ),
        models.StateRule(
            state_id="Royal Aegis",
            base_duration=float("inf"),
            trigger_tags=["HIT", "Will to Protect"],
            target_scope="TEAM",
        ),
        models.StateRule(
            state_id="Storm Anchor",
            base_duration=25.0,
            trigger_tags=["HIT", "Will to Protect"],
            target_scope="GLOBAL",
        ),
        # Will to Purge -> Maid: Cleaner (on-field CAST when Will to Cleanse == 100)
        models.StateRule(
            state_id="Cleaner Purge Count",
            base_duration=float("inf"),
            trigger_tags=["CAST", "Will to Purge"],
            required_states=["Storm Anchor", "Will to Cleanse:100", "Maid: Cleaner"],
            max_stacks=5,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Maid: Cleaner",
            base_duration=float("inf"),
            trigger_tags=["CAST", "Will to Purge"],
            required_states=["Storm Anchor", "Will to Cleanse:100"],
            termination_rules=["Will to Cleanse", "Maid: Royal Guard", "Royal Aegis", "Burst Royal Guard Enhancement"],
            target_scope="SELF",
            triggered_ability=will_to_purge_hit,
        ),
        models.StateRule(
            state_id="A4 Cleaner Stack",
            base_duration=float("inf"),
            trigger_tags=["CAST", "Will to Purge"],
            required_states=["Storm Anchor", "Will to Cleanse:100"],
            max_stacks=3,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        # 5th Will to Purge while in Maid: Cleaner destroys Storm Anchor and exits Maid: Cleaner
        models.StateRule(
            state_id="Cleaner Destroy Anchor",
            base_duration=0.0,
            trigger_tags=["CAST", "Will to Purge"],
            required_states=["Storm Anchor", "Will to Cleanse:100", "Maid: Cleaner", "Cleaner Purge Count:4"],
            termination_rules=[
                "Storm Anchor",
                "Maid: Cleaner",
                "A4 Cleaner Stack",
                "Cleaner Purge Count",
                "Burst Cleaner Enhancement",
            ],
            target_scope="GLOBAL",
        ),
        models.StateRule(
            state_id="Cleaner Destroy Aegis",
            base_duration=0.0,
            trigger_tags=["CAST", "Will to Purge"],
            required_states=["Storm Anchor", "Will to Cleanse:100", "Maid: Cleaner", "Cleaner Purge Count:4"],
            termination_rules=["Royal Aegis"],
            target_scope="TEAM",
        ),
        # Elemental Burst 20s Attendant Form Enhancements
        models.StateRule(
            state_id="Burst Attendant Window",
            base_duration=20.0,
            trigger_tags=["CAST", "Rite to Cleanse the World"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Royal Guard Enhancement",
            base_duration=20.0,
            trigger_tags=["CAST", "Rite to Cleanse the World"],
            required_states=["Maid: Royal Guard"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Royal Guard Enhancement",
            base_duration=20.0,
            trigger_tags=["HIT", "Will to Protect"],
            required_states=["Burst Attendant Window"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Cleaner Enhancement",
            base_duration=20.0,
            trigger_tags=["CAST", "Rite to Cleanse the World"],
            required_states=["Maid: Cleaner"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["CAST", "Rite to Cleanse the World"],
            required_states=["Storm Anchor", "Maid: Cleaner"],
            stacks=100,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Cleaner Enhancement",
            base_duration=20.0,
            trigger_tags=["HIT", "Will to Purge"],
            required_states=["Burst Attendant Window"],
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Will to Cleanse",
            base_duration=25.0,
            trigger_tags=["HIT", "Will to Purge"],
            required_states=["Storm Anchor", "Burst Attendant Window"],
            stacks=100,
            max_stacks=100,
            refresh_mode="REFRESH ALL",
            target_scope="SELF",
        ),
        models.StateRule(
            state_id="Burst Window Cleanup",
            base_duration=0.0,
            trigger_tags=["STATE_EXPIRE", "Burst Attendant Window"],
            termination_rules=["Burst Royal Guard Enhancement", "Burst Cleaner Enhancement"],
            target_scope="SELF",
        ),
    ]

    # --- Constellation State Rules ---
    if constellation >= 2:
        state_rules.extend([
            # Grant / reset 7 stacks of Let Us Toast on Scouring Anchor or Will to Protect
            models.StateRule(
                state_id="Let Us Toast",
                base_duration=25.0,
                trigger_tags=["CAST", "Scouring Anchor"],
                stacks=7,
                max_stacks=7,
                refresh_mode="REFRESH ALL",
                target_scope="TEAM",
            ),
            models.StateRule(
                state_id="Let Us Toast",
                base_duration=25.0,
                trigger_tags=["HIT", "Will to Protect"],
                stacks=7,
                max_stacks=7,
                refresh_mode="REFRESH ALL",
                target_scope="TEAM",
            ),
            # Consume 1 stack after dealing Stellar-Conduct reaction DMG (non-Cleaner Danica or teammates)
            models.StateRule(
                state_id="Let Us Toast Consume 1",
                base_duration=0.0,
                trigger_tags=["HIT", "Stellar-Conduct"],
                required_states=["Let Us Toast", "!Maid: Cleaner"],
                consume_stacks={"Let Us Toast": 1},
                trigger_phase="POST",
                trigger_scope="TEAM",
                target_scope="TRIGGER",
            ),
            # Danica in Maid: Cleaner consumes ALL stacks after dealing Stellar-Conduct reaction DMG
            models.StateRule(
                state_id="Let Us Toast Consume All",
                base_duration=0.0,
                trigger_tags=["HIT", "Stellar-Conduct"],
                required_states=["Maid: Cleaner", "Let Us Toast"],
                consume_stacks={"Let Us Toast": -1},
                trigger_phase="POST",
                trigger_scope="SELF",
                target_scope="SELF",
            ),
            # Track total stacks consumed party-wide; every 6 stacks refunds 1 stack to active character
            models.StateRule(
                state_id="Let Us Toast Consumed",
                base_duration=float("inf"),
                trigger_tags=["STATE_CONSUME", "Let Us Toast"],
                max_stacks=6,
                refresh_mode="REFRESH ALL",
                trigger_scope="TEAM",
                target_scope="GLOBAL",
            ),
            models.StateRule(
                state_id="Let Us Toast",
                base_duration=25.0,
                trigger_tags=["STATE_CONSUME", "Let Us Toast"],
                required_states=["Let Us Toast Consumed:5"],
                termination_rules=["Let Us Toast Consumed"],
                stacks=1,
                max_stacks=7,
                refresh_mode="REFRESH ALL",
                trigger_scope="TEAM",
                target_scope="ON_FIELD",
            ),
        ])

    if constellation >= 4:
        state_rules.extend([
            models.StateRule(
                state_id="Royal Aegis",
                base_duration=float("inf"),
                trigger_tags=["HIT", "Will to Purge"],
                required_states=["Maid: Cleaner"],
                target_scope="TEAM",
            ),
            models.StateRule(
                state_id="Cleaner Swap Out Aegis Clear",
                base_duration=0.0,
                trigger_tags=["SWAP_OUT"],
                required_states=["Maid: Cleaner"],
                termination_rules=["Royal Aegis"],
                target_scope="TEAM",
            ),
        ])

    # --- Buff Rules ---
    buff_rules = [
        # A1: Hymn of Ancient Waves (15% Electro RES Shred; +15% Electro & 30% Cryo RES Shred in Radiance: Stellar-Conduct)
        models.BuffRule(
            buff_id="DANICA_A1_ELECTRO_SHRED_BASE",
            buff_name="Hymn of Ancient Waves Electro RES Shred",
            stat="RES Shred",
            base_value=0.15,
            required_states=["Storm Anchor"],
            target_scope="TEAM",
            element_filters=["Electro"],
        ),
        models.BuffRule(
            buff_id="DANICA_A1_ELECTRO_SHRED_SC",
            buff_name="Hymn of Ancient Waves Stellar-Conduct Electro RES Shred",
            stat="RES Shred",
            base_value=0.15,
            required_states=["Storm Anchor", "Radiance: Stellar-Conduct"],
            target_scope="TEAM",
            element_filters=["Electro"],
        ),
        models.BuffRule(
            buff_id="DANICA_A1_CRYO_SHRED_SC",
            buff_name="Hymn of Ancient Waves Stellar-Conduct Cryo RES Shred",
            stat="RES Shred",
            base_value=0.30,
            required_states=["Storm Anchor", "Radiance: Stellar-Conduct"],
            target_scope="TEAM",
            element_filters=["Cryo"],
        ),
        # A4: Time to Clean House (+20% ATK in Royal Guard; +20% ATK SPD per stack in Cleaner)
        models.BuffRule(
            buff_id="DANICA_A4_ROYAL_GUARD_ATK",
            buff_name="Time to Clean House Royal Guard ATK%",
            stat="ATK%",
            base_value=0.20,
            required_states=["Maid: Royal Guard"],
            target_scope="SELF",
        ),
        models.BuffRule(
            buff_id="DANICA_A4_CLEANER_ATK_SPD",
            buff_name="Time to Clean House Cleaner ATK SPD",
            stat="ATK SPD",
            base_value=0.20,
            required_states=["A4 Cleaner Stack"],
            scale_with_stacks=True,
            target_scope="SELF",
        ),
        # P3: Stellar Jubilee (Base Stellar-Conduct DMG +0.7% per 100 ATK, max 14%)
        models.BuffRule(
            buff_id="DANICA_P3_BASE_SC_DMG",
            buff_name="Stellar Jubilee Base Stellar-Conduct DMG%",
            stat="Reaction Base DMG%",
            base_value=0.00007,
            scaling_stat="ATK",
            max_value=0.14,
            scaling_order=1,
            target_scope="TEAM",
            ability_filters=["Stellar-Conduct"],
        ),
        # Burst Form Enhancements (20s while in Attendant Form)
        models.BuffRule(
            buff_id="DANICA_BURST_ROYAL_GUARD_ATK",
            buff_name="Rite to Cleanse the World Royal Guard Flat ATK",
            stat="Flat ATK",
            base_value=burst_rg_ratio,
            required_states=["Maid: Royal Guard", "Burst Royal Guard Enhancement"],
            scaling_stat="ATK",
            max_value=burst_rg_cap,
            scaling_order=1,
            target_scope="TEAM",
        ),
        models.BuffRule(
            buff_id="DANICA_BURST_CLEANER_PURGE_DMG",
            buff_name="Rite to Cleanse the World Cleaner Will to Purge DMG%",
            stat="Elemental Skill DMG%",
            base_value=burst_cleaner_purge_dmg,
            required_states=["Maid: Cleaner", "Burst Cleaner Enhancement"],
            target_scope="SELF",
            ability_filters=["Will to Purge"],
        ),
    ]

    if constellation >= 2:
        buff_rules.extend([
            models.BuffRule(
                buff_id="DANICA_C2_TOAST_FLAT_DMG",
                buff_name="Let Us Toast Stellar-Conduct Flat DMG",
                stat="Reaction Flat DMG",
                base_value=1.00,
                required_states=["Let Us Toast", "!Maid: Cleaner"],
                scaling_stat="ATK",
                scaling_order=1,
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct"],
            ),
            models.BuffRule(
                buff_id="DANICA_C2_CLEANER_TOAST_FLAT_DMG",
                buff_name="Let Us Toast Cleaner Stellar-Conduct Flat DMG",
                stat="Reaction Flat DMG",
                base_value=1.50,
                required_states=["Maid: Cleaner", "Let Us Toast"],
                scaling_stat="ATK",
                scaling_order=1,
                target_scope="SELF",
                ability_filters=["Stellar-Conduct"],
            ),
        ])

    if constellation >= 6:
        buff_rules.extend([
            models.BuffRule(
                buff_id="DANICA_C6_SC_ELEVATION",
                buff_name="The Star That Wakes Ere Dawn Breaks Stellar-Conduct Elevation%",
                stat="Elevation%",
                base_value=0.20,
                required_states=["Storm Anchor"],
                target_scope="TEAM",
                ability_filters=["Stellar-Conduct"],
            ),
            models.BuffRule(
                buff_id="DANICA_C6_ROYAL_GUARD_ONFIELD_SC_DMG",
                buff_name="The Star That Wakes Ere Dawn Breaks Royal Guard Stellar-Conduct DMG%",
                stat="Stellar-Conduct DMG%",
                base_value=0.0001,
                required_states=["Maid: Royal Guard"],
                scaling_stat="ATK",
                max_value=0.40,
                scaling_order=1,
                target_scope="ON_FIELD",
            ),
            models.BuffRule(
                buff_id="DANICA_C6_CLEANER_PURGE_CR",
                buff_name="The Star That Wakes Ere Dawn Breaks Cleaner Will to Purge Crit Rate",
                stat="Crit Rate",
                base_value=0.00005,
                required_states=["Maid: Cleaner"],
                scaling_stat="ATK",
                max_value=0.10,
                scaling_order=1,
                target_scope="SELF",
                ability_filters=["Will to Purge"],
            ),
            models.BuffRule(
                buff_id="DANICA_C6_CLEANER_PURGE_CD",
                buff_name="The Star That Wakes Ere Dawn Breaks Cleaner Will to Purge Crit DMG",
                stat="Crit Damage",
                base_value=0.0005,
                required_states=["Maid: Cleaner"],
                scaling_stat="ATK",
                max_value=1.00,
                scaling_order=1,
                target_scope="SELF",
                ability_filters=["Will to Purge"],
            ),
        ])

    abilities = {
        "N1": n1,
        "N2": n2,
        "N3": n3,
        "N4": n4,
        "CA_Cyclic": ca_cyclic,
        "CA_Final": ca_final,
        "Plunge_Low": plunge_low,
        "Plunge_High": plunge_high,
        "SA_N1": sa_n1,
        "SA_N2": sa_n2,
        "SA_N3": sa_n3,
        "SA_N4": sa_n4,
        "Skill": skill,
        "Will_to_Protect": will_to_protect_cast,
        "Will_to_Purge": will_to_purge_cast,
        "Burst": burst,
    }

    danica = entities.Character(
        name="Danica",
        element="Electro",
        constellation=constellation,
        lvl=lvl,
        base_hp=13042.0,
        base_atk=337.0,
        base_def=776.0,
        weapon=weapon,
        artifact_set=artifact_set,
        ascension_stat={"ATK%": 0.288},
        artifact_stats=artifact_stats,
        abilities=list(abilities.values()),
        state_rules=state_rules,
        buff_rules=buff_rules,
        reaction_override={"Superconduct": "Stellar-Conduct"},
    )

    return danica, abilities