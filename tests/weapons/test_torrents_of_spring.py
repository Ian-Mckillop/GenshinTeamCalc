import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.weapons.torrents_of_spring import build_torrents_of_spring


class TestTorrentsOfSpring(unittest.TestCase):
    def setUp(self):
        # Wearer with 259 Base ATK + 741 Torrents of Spring = 1000 Base ATK
        self.weapon_r1 = build_torrents_of_spring(refinement=1)
        self.wearer_r1 = entities.Character(
            "Danica_Test", "Electro", 0, 10000, 259.0, 500, self.weapon_r1,
            weapon_type="Claymore",
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.on_field_carry = entities.Character(
            "Carry", "Cryo", 0, 10000, 1000.0, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.electro_hit = models.Ability(
            "EHit", "EHit", 1.0, element="Electro", gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.wearer_sc_hit = models.Ability(
            "WearerSC", "WearerSC", 1.0, element="Electro", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.carry_sc_probe = models.Ability(
            "CarrySC", "CarrySC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )

    def test_r1_unconditional_and_two_stage_attendants_measure(self):
        team = [self.wearer_r1, self.on_field_carry]

        # 1. Electro hit triggers Attendant's Measure:
        #    - Wearer has 1000 * (1 + 0.165 + 0.16) = 1325 ATK -> 1325 * 1.5 * 0.5 * 0.9 = 894.375
        #    - On-field carry gets +20% SC Reaction DMG% -> 1000 * 1.20 * 1.5 * 0.9 = 1620.0
        res_stage1 = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer_r1, self.electro_hit),
            simulator.RotationStep(self.on_field_carry, self.carry_sc_probe),
        ])
        self.assertAlmostEqual(res_stage1["Danica_Test"], 894.375, places=4)
        self.assertAlmostEqual(res_stage1["Carry"], 1620.0, places=4)

        # 2. Wearer hits with Stellar-Conduct DMG while Attendant's Measure is active -> Enhanced:
        #    - Wearer gains +16% more ATK (1485 ATK) and, since on-field, +40% SC Reaction DMG% -> 1485 * 1.40 * 1.5 * 0.9 = 2806.65
        #    - On-field carry also gets +40% SC Reaction DMG% -> 1000 * 1.40 * 1.5 * 0.9 = 1890.0
        res_stage2 = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer_r1, self.electro_hit),
            simulator.RotationStep(self.wearer_r1, self.wearer_sc_hit),
            simulator.RotationStep(self.on_field_carry, self.carry_sc_probe),
        ])
        self.assertAlmostEqual(res_stage2["Danica_Test"], 894.375 + 2806.65, places=4)
        self.assertAlmostEqual(res_stage2["Carry"], 1890.0, places=4)

    def test_r5_refinement_scaling(self):
        weapon_r5 = build_torrents_of_spring(refinement=5)
        wearer_r5 = entities.Character(
            "Danica_R5", "Electro", 0, 10000, 259.0, 500, weapon_r5,
            weapon_type="Claymore",
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        team = [wearer_r5, self.on_field_carry]

        # R5 Enhanced: Wearer has 1805 ATK (+80% SC DMG% while on-field), Carry gets +80% SC DMG%
        res_r5 = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(wearer_r5, self.electro_hit),
            simulator.RotationStep(wearer_r5, self.wearer_sc_hit),
            simulator.RotationStep(self.on_field_carry, self.carry_sc_probe),
        ])
        expected_wearer = 1485.0 * 1.5 * 0.5 * 0.9 + 1805.0 * 1.80 * 1.5 * 0.9
        self.assertAlmostEqual(res_r5["Danica_R5"], expected_wearer, places=4)
        self.assertAlmostEqual(res_r5["Carry"], 2430.0, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)