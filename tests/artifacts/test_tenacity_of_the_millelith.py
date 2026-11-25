import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.artifacts.tenacity_of_the_millelith import build_tenacity_of_the_millelith


class TestTenacityOfTheMillelith(unittest.TestCase):
    def setUp(self):
        self.tenacity_4pc = build_tenacity_of_the_millelith(pieces=4)
        self.wearer = entities.Character(
            "Support_Tenacity", "Electro", 0, 10000.0, 1000.0, 500.0,
            entities.Weapon("W", "Catalyst", 0.0),
            weapon_type="Catalyst",
            artifact_set=[self.tenacity_4pc],
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.teammate = entities.Character(
            "Teammate", "Cryo", 0, 10000.0, 1000.0, 500.0,
            entities.Weapon("W", "Sword", 0.0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.skill_hit = models.Ability(
            "ESkill", "ESkill", 1.0, element="Electro", attack_type="Elemental Skill",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.off_field_skill_tick = models.Ability(
            "OffFieldSkill", "OffFieldSkill", 1.0, element="Electro", attack_type="Elemental Skill",
            gauge_units=0.0, hit_offsets=[4.0], cast_duration=0.1,
        )
        self.tm_probe = models.Ability(
            "TmProbe", "TmProbe", 1.0, element="Cryo", attack_type="Normal Attack",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.idle_3_5 = models.Ability(
            "Idle35", "Idle35", 0.0, element="Physical", gauge_units=0.0, cast_duration=3.5,
        )

    def test_4pc_party_atk_and_3s_duration(self):
        # 1. Elemental Skill hit activates +20% ATK for 3.0s -> 1200 * 1.5 * 0.5 * 0.9 = 810.0
        # 2. Teammate probe at t=0.1s (within 3.0s) also gets +20% ATK -> 810.0
        # 3. After 3.5s idle (t=3.7s > 3.0s), buff expires -> Teammate probe hits at 1000 ATK -> 675.0
        res = simulator.simulate_rotation([self.wearer, self.teammate], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.skill_hit),
            simulator.RotationStep(self.teammate, self.tm_probe),
            simulator.RotationStep(self.teammate, self.idle_3_5),
            simulator.RotationStep(self.teammate, self.tm_probe),
        ])
        self.assertAlmostEqual(res["Support_Tenacity"], 810.0, places=4)
        self.assertAlmostEqual(res["Teammate"], 810.0 + 675.0, places=4)

    def test_off_field_skill_hit_retriggers_4pc(self):
        # Wearer deploys an off-field Skill hit at t=4.0s, swaps to Teammate, and waits 4.1s:
        # At t=4.0s, the off-field Skill hit triggers Tenacity 4pc -> Teammate probe at t=4.2s gets +20% ATK
        idle_4_1 = models.Ability("Idle41", "Idle41", 0.0, element="Physical", gauge_units=0.0, cast_duration=4.1)
        res = simulator.simulate_rotation([self.wearer, self.teammate], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.off_field_skill_tick),
            simulator.RotationStep(self.teammate, idle_4_1),
            simulator.RotationStep(self.teammate, self.tm_probe),
        ])
        self.assertAlmostEqual(res["Support_Tenacity"], 810.0, places=4)
        self.assertAlmostEqual(res["Teammate"], 810.0, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)