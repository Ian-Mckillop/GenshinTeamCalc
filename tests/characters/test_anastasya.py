import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.characters.anastasya import build_anastasya


class TestAnastasyaC0(unittest.TestCase):
    def setUp(self):
        # 1000 Total Base ATK (356 + 644), 100% Crit Rate, 50% base Crit DMG (canceling 38.4% CD ascension)
        self.weapon = entities.Weapon("TestBow", "Bow", 644.0)
        self.ana, self.ab = build_anastasya(
            constellation=0,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.elec_hit = models.Ability(
            "EHit", "EHit", 0.0, element="Electro", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE",
        )
        self.idle_21 = models.Ability(
            "Idle21", "Idle21", 0.0, element="Physical", gauge_units=0.0, cast_duration=21.0,
        )

    def test_character_metadata_and_default_weapon(self):
        default_ana, _ = build_anastasya()
        self.assertEqual(default_ana.weapon_type, "Bow")
        self.assertEqual(default_ana.weapon.type, "Bow")
        self.assertEqual(default_ana.base_atk, 356.0)
        self.assertEqual(default_ana.base_hp, 12736.0)
        self.assertEqual(default_ana.base_def, 779.0)

    def test_tap_skill_palestar_crown_and_a1_accolades(self):
        # Tap Skill (212.8%) + first 9 Palestar Crown ticks (18 hits) get A1 Accolades (+12% CD -> 1.62x);
        # 10th tick at t=20.0s lands right as the 20s Accolades buff expires (1.50x).
        res = simulator.simulate_rotation([self.ana, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
        ])
        expected = 1000.0 * (2.128 * 1.62 + 18 * 1.152 * 1.62 + 2 * 1.152 * 1.50) * 0.5 * 0.9
        self.assertAlmostEqual(res["Anastasya"], expected, places=3)

    def test_hold_skill_and_blessed_spear_n1_to_n5(self):
        # Hold Skill (283.7%) + Blessed Spear N1..N5 (112.9% + 118.2% + 143.5% + 159.0% + 191.4% = 725.0%)
        res = simulator.simulate_rotation([self.ana, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N1"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N2"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N3"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N4"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N5"]),
        ])
        expected = 1000.0 * (2.837 + 7.250) * 1.62 * 0.5 * 0.9
        self.assertAlmostEqual(res["Anastasya"], expected, places=3)

    def test_burst_love_sealing_and_triumph_unseal(self):
        # Trigger Stellar-Conduct (Polestar Field) -> Tap Skill -> Burst_Love -> swap out (Seals Anastasya) ->
        # wait 21s so Sealed expires -> swap Anastasya back in to trigger Palestar Edict: Triumph!
        res = simulator.simulate_rotation([self.ana, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_electro, self.elec_hit),
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Love"]),
            simulator.RotationStep(self.tm_electro, self.idle_21),
            simulator.RotationStep(self.ana, self.ab["N1"]),
        ])
        # Triumph hit has: 400.8% SC MV, +7% P3 base mult (1000 ATK), +30% Burst_Love Reaction DMG%, +12% A1 CD
        triumph_dmg = 1000.0 * 4.008 * 1.07 * 1.30 * 1.62 * 0.9
        self.assertGreater(res["Anastasya"], triumph_dmg)


class TestAnastasyaConstellations(unittest.TestCase):
    def setUp(self):
        self.weapon = entities.Weapon("TestBow", "Bow", 644.0)
        self.tm_cryo = entities.Character(
            "TM_Cryo", "Cryo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.probe_cryo = models.Ability(
            "ProbeC", "ProbeC", 1.0, element="Cryo", gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )

    def test_c1_and_c4_accolades_cryo_atk_and_cd_scaling(self):
        # At C4: Accolades gives +15.6% Crit DMG and +19.5% ATK% to Cryo teammates
        ana_c4, ab_c4 = build_anastasya(
            constellation=4,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        res = simulator.simulate_rotation([ana_c4, self.tm_cryo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c4, ab_c4["Skill_Hold"]),
            simulator.RotationStep(self.tm_cryo, self.probe_cryo),
        ])
        expected_tm = 1000.0 * 1.195 * 1.656 * 0.5 * 0.9
        self.assertAlmostEqual(res["TM_Cryo"], expected_tm, places=3)

    def test_c2_honor_125_percent_original_dmg(self):
        # C2 Honor makes Blessed Spear N1..N5 deal 125% original DMG
        ana_c2, ab_c2 = build_anastasya(
            constellation=2,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        res = simulator.simulate_rotation([ana_c2, self.tm_cryo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c2, ab_c2["Skill_Hold"]),
            simulator.RotationStep(ana_c2, ab_c2["Spear_N1"]),
        ])
        # Hold Skill (283.7% * 1.0) + Spear_N1 (112.9% * 1.25) with +15% C1 ATK% and +12% A1 CD
        expected = 1000.0 * 1.15 * (2.837 + 1.129 * 1.25) * 1.62 * 0.5 * 0.9
        self.assertAlmostEqual(res["Anastasya"], expected, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)