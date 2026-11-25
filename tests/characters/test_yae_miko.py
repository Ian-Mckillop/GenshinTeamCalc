import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.characters.yae_miko import build_yae_miko


class TestYaeMikoC0(unittest.TestCase):
    def setUp(self):
        # 1000 Total Base ATK (340 + 660), 100% Crit Rate, 50% base Crit DMG (canceling 19.2% CR ascension)
        self.weapon = entities.Weapon("TestCatalyst", "Catalyst", 660.0)
        self.yae, self.ab = build_yae_miko(
            constellation=0,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.758, "Crit Damage": 0.0},
        )
        self.tm_cryo = entities.Character(
            "TM_Cryo", "Cryo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
            reaction_override={"Superconduct": "Stellar-Conduct"},
        )
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.cryo_hit = models.Ability("CHit", "CHit", 0.0, element="Cryo", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE")
        self.idle_3 = models.Ability("Idle3", "Idle3", 0.0, element="Physical", gauge_units=0.0, cast_duration=3.0)

    def test_character_metadata_and_default_weapon(self):
        default_yae, _ = build_yae_miko()
        self.assertEqual(default_yae.weapon_type, "Catalyst")
        self.assertEqual(default_yae.weapon.type, "Catalyst")
        self.assertEqual(default_yae.base_atk, 340.0)

    def test_sesshou_sakura_scaling_and_a4_em_passive(self):
        # 1 totem ticks 8 times (every 2.8s over 24s) at Lv. 1 MV (109.2%) -> 8 * (1000 * 1.092 * 1.5 * 0.5 * 0.9) = 5896.8
        res_1 = simulator.simulate_rotation([self.yae, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.yae, self.ab["Skill_1"]),
        ])
        self.assertAlmostEqual(res_1["Yae Miko"], 5896.8, places=4)

        # With 200 EM (+30.0% Sesshou Sakura DMG% from A4): 8 * (1000 * 1.092 * 1.30 * 1.5 * 0.5 * 0.9) = 7665.84
        yae_em, ab_em = build_yae_miko(
            constellation=0,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.758, "Crit Damage": 0.0, "Elemental Mastery": 200.0},
        )
        res_em = simulator.simulate_rotation([yae_em, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(yae_em, ab_em["Skill_1"]),
        ])
        self.assertAlmostEqual(res_em["Yae Miko"], 7665.84, places=4)

    def test_three_totems_a1_fourth_cast_and_burst_tenko_thunderbolts(self):
        # 3 Skill casts + Burst before t=2.8s: no A1 strike yet, Burst consumes all 3 totems (468% + 3 * 601%)
        res_3_casts = simulator.simulate_rotation([self.yae, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.yae, self.ab["Skill_1"]),
            simulator.RotationStep(self.yae, self.ab["Skill_2"]),
            simulator.RotationStep(self.yae, self.ab["Skill_3"]),
            simulator.RotationStep(self.yae, self.ab["Burst"]),
        ])
        expected_3 = 1000.0 * (4.68 + 3 * 6.01) * 1.5 * 0.5 * 0.9
        self.assertAlmostEqual(res_3_casts["Yae Miko"], expected_3, places=4)

        # 4th Skill cast while 3 totems already exist triggers A1 40% strike, then Burst consumes all 3 totems
        res_4_casts = simulator.simulate_rotation([self.yae, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.yae, self.ab["Skill_1"]),
            simulator.RotationStep(self.yae, self.ab["Skill_2"]),
            simulator.RotationStep(self.yae, self.ab["Skill_3"]),
            simulator.RotationStep(self.yae, self.ab["Skill_1"]),
            simulator.RotationStep(self.yae, self.ab["Burst"]),
        ])
        expected_4 = 1000.0 * (0.40 + 4.68 + 3 * 6.01) * 1.5 * 0.5 * 0.9
        self.assertAlmostEqual(res_4_casts["Yae Miko"], expected_4, places=4)

    def test_edict_of_cleansing_polestar_enhancement(self):
        # Trigger Stellar-Conduct (Polestar Field) -> Yae enters Radiance: Stellar-Conduct.
        # Tick 1 (t=3.25s) gets +80% ATK Flat DMG AND fires a 200% ATK Stellar-Conduct bolt;
        # Tick 2 (t=6.05s) gets +31% Electro DMG% from Polestar Field; ticks 3..8 hit normally.
        res = simulator.simulate_rotation([self.yae, self.tm_cryo], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_cryo, self.cryo_hit),
            simulator.RotationStep(self.yae, self.ab["N1"]),
            simulator.RotationStep(self.yae, self.ab["Skill_1"]),
        ])
        n1_dmg = 1000.0 * 0.714 * 1.5 * 0.5 * 0.9
        tick1_dmg = 1000.0 * (1.092 + 0.80) * 1.5 * 0.5 * 0.9
        edict_bolt_dmg = 1000.0 * 2.00 * 1.5 * 0.9
        tick2_polestar_dmg = 1000.0 * 1.092 * 1.30 * 1.5 * 0.5 * 0.9
        other_ticks_dmg = 6 * (1000.0 * 1.092 * 1.5 * 0.5 * 0.9)
        self.assertAlmostEqual(
            res["Yae Miko"],
            n1_dmg + tick1_dmg + edict_bolt_dmg + tick2_polestar_dmg + other_ticks_dmg,
            places=3,
        )


class TestYaeMikoConstellations(unittest.TestCase):
    def setUp(self):
        self.weapon = entities.Weapon("TestCatalyst", "Catalyst", 660.0)
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.probe_elec = models.Ability("ProbeE", "ProbeE", 1.0, element="Electro", gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1)
        self.idle_3 = models.Ability("Idle3", "Idle3", 0.0, element="Physical", gauge_units=0.0, cast_duration=3.0)

    def test_c2_em_sharing_and_level_scaling(self):
        yae_c2, ab_c2 = build_yae_miko(
            constellation=2,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.758, "Crit Damage": 0.0},
        )
        # 1 totem at C2 starts at Lv. 2 (136.5%) and grants +90 EM (+13.5% A4 Sakura DMG%) across 8 ticks
        res_c2 = simulator.simulate_rotation([yae_c2, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(yae_c2, ab_c2["Skill_1"]),
        ])
        expected_c2 = 8 * (1000.0 * 1.365 * 1.135 * 1.5 * 0.5 * 0.9)
        self.assertAlmostEqual(res_c2["Yae Miko"], expected_c2, places=4)

    def test_c4_party_electro_dmg_and_burst_dmg(self):
        yae_c4, ab_c4 = build_yae_miko(
            constellation=4,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.758, "Crit Damage": 0.0},
        )
        res = simulator.simulate_rotation([yae_c4, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(yae_c4, ab_c4["Skill_1"]),
            simulator.RotationStep(yae_c4, self.idle_3),
            simulator.RotationStep(self.tm_electro, self.probe_elec),
        ])
        self.assertAlmostEqual(res["TM_Electro"], 810.0, places=4)

    def test_c6_def_ignore_and_stellar_conduct_crit_dmg(self):
        yae_c6, ab_c6 = build_yae_miko(
            constellation=6,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.758, "Crit Damage": 0.0},
        )
        res = simulator.simulate_rotation([yae_c6, self.tm_electro], entities.Enemy(lvl=90), [
            simulator.RotationStep(yae_c6, ab_c6["Skill_1"]),
            simulator.RotationStep(yae_c6, ab_c6["Skill_2"]),
            simulator.RotationStep(yae_c6, ab_c6["Skill_3"]),
        ])
        def_mult_c6 = 190.0 / (190.0 + 190.0 * 0.40)
        sakura_24_dmg = 24 * (1000.0 * 2.518 * 1.50 * 1.5 * def_mult_c6 * 0.9)
        self.assertAlmostEqual(res["Yae Miko"], sakura_24_dmg, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)