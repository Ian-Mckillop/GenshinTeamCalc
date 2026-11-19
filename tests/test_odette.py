import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.characters.odette import build_odette


class TestOdetteC0(unittest.TestCase):
    def setUp(self):
        # 1000 Total Base ATK (335 + 665), 100% Crit Rate, 50% base Crit DMG (canceling 38.4% ascension)
        self.weapon = entities.Weapon("TestSword", "Sword", 665.0)
        self.odette, self.ab = build_odette(
            constellation=0,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.tm_anemo = entities.Character(
            "TM_Anemo", "Anemo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.probe_sc = models.Ability(
            "ProbeSC", "ProbeSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.idle_2_5 = models.Ability("Idle2.5", "Idle2.5", 0.0, element="Physical", gauge_units=0.0, cast_duration=2.5)
        self.idle_25 = models.Ability("Idle25", "Idle25", 0.0, element="Physical", gauge_units=0.0, cast_duration=25.0)

    def test_character_metadata_and_default_weapon(self):
        default_odette, _ = build_odette()
        self.assertEqual(default_odette.weapon_type, "Sword")
        self.assertEqual(default_odette.weapon.type, "Sword")
        self.assertEqual(default_odette.base_atk, 335.0)

    def test_marvelous_splendor_off_field_transfer_and_a4_scaling(self):
        # Give Odette +100% ATK (2000 total ATK):
        # - P3: +14% Reaction Base DMG% (0.00007 * 2000 = 0.14)
        # - A4: +15% Original DMG Mult (0.00015 * (2000 - 1000) = 0.15 -> 1.15x)
        # - A1: 4 stacks of Marvelous Splendor = +60% Reaction DMG%
        odette_2k, ab_2k = build_odette(
            constellation=0,
            weapon=self.weapon,
            artifact_stats={"ATK%": 1.0, "Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        team = [odette_2k, self.tm_electro, self.tm_anemo]

        # 1. On-field Odette deals Stellar-Conduct Probe after Skill (4 stacks = +60% Reaction DMG%)
        # Note: simulate_rotation also processes all 20s of Solo Dance Double ticks (5 Plume + 4 Wing)
        res_on_field = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(odette_2k, ab_2k["Skill"]),
            simulator.RotationStep(odette_2k, self.probe_sc),
        ])
        expected_odette_probe = 2000.0 * 1.0 * 1.15 * 1.14 * 1.60 * 1.5 * 0.9
        skill_dmg = 2000.0 * 1.945 * 1.5 * 0.5 * 0.9
        dance_double_dmg = 2000.0 * (5 * 0.775 + 4 * 0.926) * 1.5 * 0.5 * 0.9
        self.assertAlmostEqual(res_on_field["Odette"] - skill_dmg - dance_double_dmg, expected_odette_probe, places=3)

        # 2. Swap to TM_Electro and wait 2.5s off-field -> 2 stacks transferred to TM_Electro (+30% Reaction DMG%)
        res_transfer = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(odette_2k, ab_2k["Skill"]),
            simulator.RotationStep(self.tm_electro, self.idle_2_5),
            simulator.RotationStep(self.tm_electro, self.probe_sc),
        ])
        # TM_Electro has 1000 ATK, P3 +14% Base DMG%, 2 stacks MS (+30% Reaction DMG%)
        expected_tm_probe = 1000.0 * 1.0 * 1.14 * 1.30 * 1.5 * 0.9
        self.assertAlmostEqual(res_transfer["TM_Electro"], expected_tm_probe, places=3)

    def test_coda_special_skill_and_post_coda_dance_double_enhancement(self):
        electro_hit = models.Ability("EHit", "EHit", 0.0, element="Electro", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE")
        team = [self.odette, self.tm_electro, self.tm_anemo]

        # Without Coda: Solo Dance Double deals 5 Plume (77.5%) + 4 Wing (92.6%) over 20s
        res_no_coda = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_electro, electro_hit),
            simulator.RotationStep(self.odette, self.ab["Skill"]),
            simulator.RotationStep(self.odette, self.idle_25),
        ])
        # With Coda: deals Coda DoT + 550% Stellar-Conduct Finale + adds SC hits to all Plume/Wing moves
        res_with_coda = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_electro, electro_hit),
            simulator.RotationStep(self.odette, self.ab["Skill"]),
            simulator.RotationStep(self.odette, self.ab["Skill_Coda"]),
            simulator.RotationStep(self.odette, self.idle_25),
        ])
        self.assertGreater(res_with_coda["Odette"] - res_no_coda["Odette"], 18000.0)


class TestOdetteConstellations(unittest.TestCase):
    def setUp(self):
        self.weapon = entities.Weapon("TestSword", "Sword", 665.0)
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.tm_anemo = entities.Character(
            "TM_Anemo", "Anemo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.probe_sc = models.Ability(
            "ProbeSC", "ProbeSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.idle_3_5 = models.Ability("Idle3.5", "Idle3.5", 0.0, element="Physical", gauge_units=0.0, cast_duration=3.5)

    def test_c1_c2_and_c6_marvelous_splendor_scaling(self):
        odette_c2, ab_c2 = build_odette(
            constellation=2,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        team_c2 = [odette_c2, self.tm_electro, self.tm_anemo]

        # At C2, Odette starts with 6 stacks of Marvelous Splendor (+90% Reaction DMG%, +42% ATK% -> 1420 ATK)
        # Wait 3.5s off-field -> all 6 stacks transferred at 2/sec to TM_Electro (1420 ATK, +90% Reaction DMG%)
        res_c2 = simulator.simulate_rotation(team_c2, entities.Enemy(lvl=90), [
            simulator.RotationStep(odette_c2, ab_c2["Skill"]),
            simulator.RotationStep(self.tm_electro, self.idle_3_5),
            simulator.RotationStep(self.tm_electro, self.probe_sc),
        ])
        # P3 uses Odette's ATK (1000 -> +7% Base DMG%), TM_Electro has 1420 ATK, +90% Reaction DMG%
        expected_tm_c2 = 1420.0 * 1.0 * 1.07 * 1.90 * 1.5 * 0.9
        self.assertAlmostEqual(res_c2["TM_Electro"], expected_tm_c2, places=3)

        # At C6, Odette keeps all 6 stacks even after transferring 6 stacks to teammates, and gains +45% Elevation
        odette_c6, ab_c6 = build_odette(
            constellation=6,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        team_c6 = [odette_c6, self.tm_electro, self.tm_anemo]
        res_c6 = simulator.simulate_rotation(team_c6, entities.Enemy(lvl=90), [
            simulator.RotationStep(odette_c6, ab_c6["Skill"]),
            simulator.RotationStep(self.tm_electro, self.idle_3_5),
            simulator.RotationStep(odette_c6, self.probe_sc),
        ])
        # Odette has 1420 ATK (+42% ATK%), +9.94% P3 Base DMG%, +6.3% A4 Original DMG, +90% Reaction DMG%, +45% Elevation
        # Odette has 1420 ATK (+42% ATK%), +9.94% P3 Base DMG%, +6.3% A4 Original DMG, +90% Reaction DMG%, +45% Elevation
        # Odette has 1420 ATK (+42% ATK%), +9.94% P3 Base DMG%, +6.3% A4 Original DMG, +90% Reaction DMG%, +45% Elevation
        # Note: C6 also includes C3 (+3 Skill levels: 2.295 Skill, 0.914 Plume, 1.093 Wing) and C4 Coordinated Attacks (0.660 SC)
        skill_dmg = 1420.0 * 2.295 * 1.5 * 0.5 * 0.9
        dance_double_dmg = 1420.0 * (5 * 0.914 + 4 * 1.093) * 1.5 * 0.5 * 0.9
        expected_odette_probe_c6 = 1420.0 * 1.0 * (1.0 + 0.00015 * 420.0) * (
                    1.0 + 0.00007 * 1420.0) * 1.90 * 1.5 * 0.9 * 1.45
        expected_c4_coord_c6 = 0.660 * expected_odette_probe_c6
        self.assertAlmostEqual(
            res_c6["Odette"] - skill_dmg - dance_double_dmg - 5 * expected_c4_coord_c6,
            expected_odette_probe_c6,
            places=2,
        )

    def test_c4_team_snow_swan_dream_and_coordinated_attack(self):
        odette_c4, ab_c4 = build_odette(
            constellation=4,
            weapon=self.weapon,
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384},
        )
        team = [odette_c4, self.tm_electro, self.tm_anemo]

        res = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(odette_c4, ab_c4["Burst"]),
            simulator.RotationStep(self.tm_electro, self.probe_sc),
        ])
        # TM_Electro gets +25% Reaction DMG% from C4 Snow Swan's Dream (50% of 50%), and P3 scales off Odette's 1420 ATK (+9.94%)
        expected_tm = 1000.0 * 1.0 * (1.0 + 0.00007 * 1420.0) * 1.25 * 1.5 * 0.9
        self.assertAlmostEqual(res["TM_Electro"], expected_tm, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)