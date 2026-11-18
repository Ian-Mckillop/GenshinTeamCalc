import unittest
import engine.entities as entities
import engine.models as models
from engine.simulator import RotationStep, simulate_rotation


# --- Test Helpers ---

def make_ability(
    name: str,
    element: str,
    mv: float = 0.0,
    gauge_units: float = 1.0,
    attack_type: str = "Elemental Skill",
    scaling_stat: str = "ATK",
    is_blunt: bool = False,
    tags: list[str] | None = None,
    hit_offsets: list[float] | None = None,
    cast_duration: float = 0.1,
) -> models.Ability:
    return models.Ability(
        parent_name=name,
        component_name=name,
        mv=mv,
        element=element,
        attack_type=attack_type,
        scaling_stat=scaling_stat,
        gauge_units=gauge_units,
        icd_group="NONE",
        is_blunt=is_blunt,
        tags=tags or [],
        hit_offsets=hit_offsets if hit_offsets is not None else [0.0],
        sub_abilities=[],
        cast_duration=cast_duration,
    )


def make_char(
    name: str,
    element: str = "Pyro",
    lvl: int = 90,
    atk: float = 1000.0,
    em: float = 0.0,
    crit_rate: float = 0.0,
    crit_dmg: float = 0.50,
    reaction_override: dict[str, str] | None = None,
    state_rules: list[entities.StateRule] | None = None,
    buff_rules: list[entities.BuffRule] | None = None,
    polestar_bonus_stacks: int = 0,
    polestar_instant_buff: bool = False,
    instant_lv2_vortex: bool = False,
    lunar_domain_a4: bool = False,
) -> entities.Character:
    """Builds a minimal Character matching entities.Character with deterministic 0% Crit Rate by default."""
    dummy_weapon = entities.Weapon(name="Test Weapon", type="Sword", base_atk=0.0)
    # Offset Character.out_of_combat_stats() default 5% Crit Rate and 50% Crit Damage
    base_art_stats = {
        "Crit Rate": crit_rate - 0.05,
        "Crit Damage": crit_dmg - 0.50,
        "Elemental Mastery": em,
    }
    return entities.Character(
        name=name,
        element=element,
        constellation=0,
        base_hp=10000.0,
        base_atk=atk,
        base_def=500.0,
        weapon=dummy_weapon,
        lvl=lvl,
        artifact_set=[],
        artifact_stats=base_art_stats,
        reaction_override=reaction_override or {},
        state_rules=state_rules or [],
        buff_rules=buff_rules or [],
        polestar_bonus_stacks=polestar_bonus_stacks,
        polestar_instant_buff=polestar_instant_buff,
        instant_lv2_vortex=instant_lv2_vortex,
        lunar_domain_a4=lunar_domain_a4,
    )


def make_enemy(lvl: int = 90, base_res: float = 0.10) -> entities.Enemy:
    elements = ("Pyro", "Hydro", "Cryo", "Electro", "Dendro", "Anemo", "Geo", "Physical")
    return entities.Enemy(
        lvl=lvl,
        resistances={el: base_res for el in elements},
        auras={},
        last_aura_time=0.0,
    )


# --- Reaction Verification Suite ---

class TestReactionEngine(unittest.TestCase):
    # Level 90 multiplier (1446.85) * 10% RES multiplier (0.9) = 1302.165
    LVL90_RES10_BASE = 1446.85 * 0.9

    def test_amplifying_vaporize_and_reverse_melt(self):
        pyro = make_char("PyroUnit", element="Pyro", atk=1000.0)
        hydro = make_char("HydroUnit", element="Hydro", atk=1000.0)
        cryo = make_char("CryoUnit", element="Cryo", atk=1000.0)

        hydro_prime = make_ability("HydroPrime", "Hydro", mv=0.0, gauge_units=2.0)
        pyro_nuke = make_ability("PyroNuke", "Pyro", mv=1.0, gauge_units=1.0)
        cryo_hit = make_ability("CryoHit", "Cryo", mv=1.0, gauge_units=1.0)

        # Unreacted Pyro 100% MV hit
        raw_res = simulate_rotation([pyro], make_enemy(), [RotationStep(pyro, pyro_nuke)])
        raw_dmg = raw_res["PyroUnit"]

        # Reverse Vaporize (1.5x): Hydro aura -> Pyro trigger
        vape_res = simulate_rotation(
            [hydro, pyro],
            make_enemy(),
            [RotationStep(hydro, hydro_prime), RotationStep(pyro, pyro_nuke)],
        )
        self.assertAlmostEqual(vape_res["PyroUnit"], raw_dmg * 1.5, places=4)

        # Reverse Melt (1.5x): Pyro aura -> Cryo trigger
        rmelt_res = simulate_rotation(
            [pyro, cryo],
            make_enemy(),
            [RotationStep(pyro, pyro_nuke), RotationStep(cryo, cryo_hit)],
        )
        self.assertAlmostEqual(rmelt_res["CryoUnit"], raw_dmg * 1.5, places=4)

    def test_quicken_aggravate_and_spread(self):
        dendro = make_char("DendroUnit", element="Dendro", atk=1000.0)
        electro = make_char("ElectroUnit", element="Electro", atk=1000.0)

        dendro_0 = make_ability("Dendro0", "Dendro", mv=0.0, gauge_units=1.0)
        electro_0 = make_ability("Electro0", "Electro", mv=0.0, gauge_units=1.0)

        # Quicken setup (0 MV) -> Aggravate (1.15 coeff * 0.5 DEF mult) -> Spread (1.25 coeff * 0.5 DEF mult)
        res = simulate_rotation(
            [dendro, electro],
            make_enemy(lvl=90),
            [
                RotationStep(dendro, dendro_0),
                RotationStep(electro, electro_0),
                RotationStep(electro, electro_0),
                RotationStep(dendro, dendro_0),
            ],
        )
        self.assertAlmostEqual(res["ElectroUnit"], self.LVL90_RES10_BASE * 1.15 * 0.5, places=3)
        self.assertAlmostEqual(res["DendroUnit"], self.LVL90_RES10_BASE * 1.25 * 0.5, places=3)

    def test_transformative_overloaded_and_shattered(self):
        pyro = make_char("PyroUnit", element="Pyro")
        electro = make_char("ElectroUnit", element="Electro")
        hydro = make_char("HydroUnit", element="Hydro")
        cryo = make_char("CryoUnit", element="Cryo")
        claymore = make_char("ClaymoreUnit", element="Physical")

        # Overloaded (2.75 coeff)
        ovl_res = simulate_rotation(
            [pyro, electro],
            make_enemy(),
            [
                RotationStep(pyro, make_ability("Pyro0", "Pyro", mv=0.0)),
                RotationStep(electro, make_ability("Electro0", "Electro", mv=0.0)),
            ],
        )
        self.assertAlmostEqual(ovl_res["ElectroUnit"], self.LVL90_RES10_BASE * 2.75, places=3)

        # Frozen -> Shattered (3.0 coeff via blunt Physical 0 MV hit)
        shatter_res = simulate_rotation(
            [hydro, cryo, claymore],
            make_enemy(),
            [
                RotationStep(hydro, make_ability("Hydro0", "Hydro", mv=0.0)),
                RotationStep(cryo, make_ability("Cryo0", "Cryo", mv=0.0)),
                RotationStep(claymore, make_ability("Blunt0", "Physical", mv=0.0, gauge_units=0.0, is_blunt=True)),
            ],
        )
        self.assertAlmostEqual(shatter_res["ClaymoreUnit"], self.LVL90_RES10_BASE * 3.0, places=3)

    def test_electro_charged_and_burning_ticks(self):
        hydro = make_char("HydroUnit", element="Hydro")
        electro = make_char("ElectroUnit", element="Electro")

        # Hydro 2U (1.6 GU at t=0.0) + Electro 1U (0.8 GU at t=0.1):
        # Tick 1 at t=0.1 drains 0.4 GU (0.4 left); Tick 2 at t=1.1 drains 0.4 GU -> depleted (2 ticks * 2.0 coeff)
        ec_res = simulate_rotation(
            [hydro, electro],
            make_enemy(),
            [
                RotationStep(hydro, make_ability("Hydro2U", "Hydro", mv=0.0, gauge_units=2.0, cast_duration=0.1)),
                RotationStep(electro, make_ability("Electro1U", "Electro", mv=0.0, gauge_units=1.0, cast_duration=0.1)),
            ],
        )
        self.assertAlmostEqual(ec_res["ElectroUnit"], 2 * self.LVL90_RES10_BASE * 2.0, places=3)

        # Burning: Dendro 1U (0.8 GU at t=0.0) + Pyro 1U (at t=0.1) -> 6 ticks at 0.25s intervals (0.25 coeff each)
        dendro = make_char("DendroUnit", element="Dendro")
        pyro = make_char("PyroUnit", element="Pyro")
        burn_res = simulate_rotation(
            [dendro, pyro],
            make_enemy(),
            [
                RotationStep(dendro, make_ability("Dendro1U", "Dendro", mv=0.0, gauge_units=1.0, cast_duration=0.1)),
                RotationStep(pyro, make_ability("Pyro1U", "Pyro", mv=0.0, gauge_units=1.0, cast_duration=0.1)),
            ],
        )
        self.assertAlmostEqual(burn_res["PyroUnit"], 6 * self.LVL90_RES10_BASE * 0.25, places=3)

    def test_bloom_overflow_and_hyperbloom(self):
        dendro = make_char("DendroUnit", element="Dendro")
        hydro = make_char("HydroUnit", element="Hydro")
        electro = make_char("ElectroUnit", element="Electro")

        # 6 Blooms before 6.0s -> 6th core forces 1st core to explode immediately (2.0 coeff),
        # remaining 5 explode at t=6.0s -> 6 total Bloom explosions
        steps = []
        for _ in range(6):
            steps.append(RotationStep(dendro, make_ability("Dendro2U", "Dendro", mv=0.0, gauge_units=2.0, cast_duration=0.05)))
            steps.append(RotationStep(hydro, make_ability("Hydro1U", "Hydro", mv=0.0, gauge_units=1.0, cast_duration=0.05)))

        bloom_res = simulate_rotation([dendro, hydro], make_enemy(), steps)
        self.assertAlmostEqual(bloom_res["HydroUnit"], 6 * self.LVL90_RES10_BASE * 2.0, places=3)

        # 3 Blooms + 1 Electro hit -> detonates 2 cores via Hyperbloom (3.0 coeff each), 1 expires as Bloom (2.0 coeff)
        hb_steps = steps[:6] + [
            RotationStep(electro, make_ability("Electro0", "Electro", mv=0.0, gauge_units=0.0, cast_duration=0.1))
        ]
        hb_res = simulate_rotation([dendro, hydro, electro], make_enemy(), hb_steps)
        self.assertAlmostEqual(hb_res["ElectroUnit"], 2 * self.LVL90_RES10_BASE * 3.0, places=3)
        self.assertAlmostEqual(hb_res["HydroUnit"], 1 * self.LVL90_RES10_BASE * 2.0, places=3)

    def test_stellar_conduct_and_anastasya_a4(self):
        anastasya_buffs = [
            entities.BuffRule(
                buff_id="ANASTASYA_SWIRL_BASE",
                buff_name="Anastasya Stellar Swirl Base DMG%",
                character_source="Anastasya",
                stat="Reaction Base DMG%",
                base_value=0.15,
                target_scope="TEAM",
                ability_filters=["Stellar Swirl"],
            )
        ]
        anastasya = make_char(
            "Anastasya",
            element="Cryo",
            atk=1000.0,
            reaction_override={"Superconduct": "Stellar-Conduct", "Swirl": "Stellar Swirl"},
            buff_rules=anastasya_buffs,
            polestar_bonus_stacks=1,
            polestar_instant_buff=True,
            instant_lv2_vortex=True,
        )
        electro = make_char("ElectroUnit", element="Electro", atk=1000.0)
        phys = make_char("PhysUnit", element="Physical", atk=1000.0)

        phys_hit = make_ability("PhysHit", "Physical", mv=1.0, gauge_units=0.0)
        cryo_talent_hit = make_ability("CryoTalent", "Cryo", mv=1.0, gauge_units=0.0)
        direct_sc_hit = make_ability(
            "DirectSC",
            "Cryo",
            mv=1.0,
            gauge_units=0.0,
            attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"],
        )

        # Baselines before Polestar Field
        base_phys = simulate_rotation([phys], make_enemy(), [RotationStep(phys, phys_hit)])["PhysUnit"]
        base_cryo = simulate_rotation([electro], make_enemy(), [RotationStep(electro, cryo_talent_hit)])["ElectroUnit"]
        base_dsc = simulate_rotation([anastasya], make_enemy(), [RotationStep(anastasya, direct_sc_hit)])["Anastasya"]

        # Trigger Stellar-Conduct with Anastasya:
        # 1) Physical RES drops from 10% to -30% -> res_mult goes from 0.90 to 1.15 (1.15 / 0.90x)
        # 2) Polestar activates immediately at 1 stack -> +29% Cryo DMG% on talent hits (1.29x)
        #    and +0.45 Base Reaction Coefficient on Direct Stellar-Conduct hits (1.45x)
        sc_res = simulate_rotation(
            [anastasya, electro, phys],
            make_enemy(),
            [
                RotationStep(electro, make_ability("Electro0", "Electro", mv=0.0, cast_duration=0.1)),
                RotationStep(anastasya, make_ability("Cryo0", "Cryo", mv=0.0, cast_duration=0.1)),
                RotationStep(phys, phys_hit),
                RotationStep(electro, cryo_talent_hit),
                RotationStep(anastasya, direct_sc_hit),
            ],
        )
        self.assertAlmostEqual(sc_res["PhysUnit"], base_phys * (1.15 / 0.90), places=3)
        self.assertAlmostEqual(sc_res["ElectroUnit"], base_cryo * 1.29, places=3)
        self.assertAlmostEqual(sc_res["Anastasya"], base_dsc * 1.45, places=3)

    def test_stellar_swirl_and_vortex_detonation(self):
        anastasya_buffs = [
            entities.BuffRule(
                buff_id="ANASTASYA_SWIRL_BASE",
                buff_name="Anastasya Stellar Swirl Base DMG%",
                character_source="Anastasya",
                stat="Reaction Base DMG%",
                base_value=0.15,
                target_scope="TEAM",
                ability_filters=["Stellar Swirl"],
            )
        ]
        anastasya = make_char(
            "Anastasya",
            element="Cryo",
            reaction_override={"Swirl": "Stellar Swirl"},
            buff_rules=anastasya_buffs,
            instant_lv2_vortex=True,
        )
        anemo = make_char("AnemoUnit", element="Anemo")

        # Single Stellar Swirl with Anastasya:
        # Immediate hit: 0.75 * 1.15 coeff Anemo; Vortex (instant Lv. 2): 3.0 * 1.15 coeff Cryo at t=3.1s
        # Both contributors have identical stats -> weighted sum = (0.6 + 0.3) = 0.9x single-roll DMG
        ss_res = simulate_rotation(
            [anastasya, anemo],
            make_enemy(),
            [
                RotationStep(anastasya, make_ability("Cryo0", "Cryo", mv=0.0, cast_duration=0.1)),
                RotationStep(anemo, make_ability("Anemo0", "Anemo", mv=0.0, cast_duration=0.1)),
            ],
        )
        expected_ss = 0.9 * self.LVL90_RES10_BASE * (0.75 + 3.0) * 1.15
        self.assertAlmostEqual(ss_res["AnemoUnit"], expected_ss, places=3)

        # 6 Stellar Swirls within 3.0s -> early detonation on 6th trigger, no duplicate explosion at t=3.0s
        six_steps = []
        for _ in range(6):
            six_steps.append(RotationStep(anastasya, make_ability("Cryo1", "Cryo", mv=0.0, gauge_units=1.0, cast_duration=0.1)))
            six_steps.append(RotationStep(anemo, make_ability("Anemo1", "Anemo", mv=0.0, gauge_units=2.0, cast_duration=0.1)))

        six_res = simulate_rotation([anastasya, anemo], make_enemy(), six_steps)
        expected_six = 0.9 * self.LVL90_RES10_BASE * (6 * 0.75 + 3.0) * 1.15
        self.assertAlmostEqual(six_res["AnemoUnit"], expected_six, places=3)

    def test_lunar_reactions_and_columbina_a4(self):
        lunar_domain_rule = entities.StateRule(
            state_id="Lunar Domain",
            character_source="Columbina",
            trigger_tags=["CAST", "Elemental Burst"],
            required_states=[],
            base_duration=20.0,
            refresh_mode="REFRESH ALL",
            max_stacks=1,
        )
        columbina = make_char(
            "Columbina",
            element="Hydro",
            reaction_override={
                "Electro-Charged": "Lunar-Charged",
                "Bloom": "Lunar-Bloom",
                "Crystallize": "Lunar-Crystallize",
            },
            state_rules=[lunar_domain_rule],
            lunar_domain_a4=True,
        )
        electro = make_char("ElectroUnit", element="Electro")
        geo = make_char("GeoUnit", element="Geo")
        dendro = make_char("DendroUnit", element="Dendro")

        # 1) Lunar-Charged without Domain: 3 Thundercloud strikes (t=2.1s, 4.1s, 6.1s) * 1.8 coeff
        # Two equal contributors -> weight sum = (1.0 + 0.5) = 1.5x
        lc_base = simulate_rotation(
            [columbina, electro],
            make_enemy(),
            [
                RotationStep(columbina, make_ability("Hydro2U", "Hydro", mv=0.0, gauge_units=2.0, cast_duration=0.1)),
                RotationStep(electro, make_ability("Electro2U", "Electro", mv=0.0, gauge_units=2.0, cast_duration=0.1)),
            ],
        )
        expected_lc_base = 3 * 1.5 * self.LVL90_RES10_BASE * 1.8
        self.assertAlmostEqual(lc_base["ElectroUnit"], expected_lc_base, places=3)

        # 2) Lunar-Charged WITH Columbina Burst (Lunar Domain): 1.33x expected strikes
        burst_step = make_ability("ColumbinaBurst", "Hydro", mv=0.0, gauge_units=0.0, attack_type="Elemental Burst", cast_duration=0.1)
        lc_domain = simulate_rotation(
            [columbina, electro],
            make_enemy(),
            [
                RotationStep(columbina, burst_step),
                RotationStep(columbina, make_ability("Hydro2U", "Hydro", mv=0.0, gauge_units=2.0, cast_duration=0.1)),
                RotationStep(electro, make_ability("Electro2U", "Electro", mv=0.0, gauge_units=2.0, cast_duration=0.1)),
            ],
        )
        self.assertAlmostEqual(lc_domain["ElectroUnit"], expected_lc_base * 1.33, places=3)

        # 3) Lunar-Crystallize: 3 triggers -> Moondrift Harmony fires 3 projectiles * 0.96 coeff (* 1.33 in Domain)
        lcrys_steps = [RotationStep(columbina, burst_step)]
        for _ in range(3):
            lcrys_steps.append(RotationStep(columbina, make_ability("Hydro1U", "Hydro", mv=0.0, gauge_units=1.0, cast_duration=0.1)))
            lcrys_steps.append(RotationStep(geo, make_ability("Geo1U", "Geo", mv=0.0, gauge_units=2.0, cast_duration=0.1)))

        lcrys_res = simulate_rotation([columbina, geo], make_enemy(), lcrys_steps)
        expected_lcrys = 3 * 1.33 * 1.5 * self.LVL90_RES10_BASE * 0.96
        self.assertAlmostEqual(lcrys_res["GeoUnit"], expected_lcrys, places=3)

        # 4) Lunar-Bloom: generates Verdant Dew (at t=2.7s) & Moonridge Dew (immediately at t=0.2s in Domain)
        dew_check_buff = entities.BuffRule(
            buff_id="DEW_VERIFY",
            buff_name="Dew Check",
            character_source="Columbina",
            stat="All DMG%",
            base_value=1.0,
            target_scope="SELF",
            required_states=["Verdant Dew", "Moonridge Dew"],
        )
        columbina.buff_rules.append(dew_check_buff)
        test_hit = make_ability("TestHit", "Hydro", mv=1.0, gauge_units=0.0, cast_duration=0.1)

        control = make_char("Control", element="Hydro", atk=1000.0)
        raw_hit = simulate_rotation([control], make_enemy(), [RotationStep(control, test_hit)])["Control"]
        lb_res = simulate_rotation(
            [columbina, dendro],
            make_enemy(),
            [
                RotationStep(columbina, burst_step),
                RotationStep(dendro, make_ability("Dendro1U", "Dendro", mv=0.0, gauge_units=1.0, cast_duration=0.1)),
                RotationStep(columbina, make_ability("Hydro1U", "Hydro", mv=0.0, gauge_units=1.0, cast_duration=3.0)),
                RotationStep(columbina, test_hit),
            ],
        )
        # Bloom explosion (2.0 coeff) + test_hit with +100% All DMG% (2.0x raw_hit)
        expected_lb = (self.LVL90_RES10_BASE * 2.0) + (raw_hit * 2.0)
        self.assertAlmostEqual(lb_res["Columbina"], expected_lb, places=3)


if __name__ == "__main__":
    unittest.main()