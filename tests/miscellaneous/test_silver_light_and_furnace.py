import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.artifacts.heart_of_the_furnace import build_heart_of_the_furnace
from data.weapons.silver_light import build_silver_light


class TestSilverLightAndHeartOfTheFurnace(unittest.TestCase):
    def setUp(self):
        # Wearer with 490 Base ATK + 510 Silver Light = 1000 Base ATK
        self.weapon_r5 = build_silver_light(refinement=5)
        self.furnace_4pc = build_heart_of_the_furnace(pieces=4)
        self.wearer = entities.Character(
            "Odette_Test", "Cryo", 0, 10000, 490.0, 500, self.weapon_r5,
            weapon_type="Sword",
            artifact_set=[self.furnace_4pc],
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.teammate = entities.Character(
            "Teammate", "Electro", 0, 10000, 1000.0, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.skill_cast = models.Ability(
            "ESkill", "ESkill", 1.0, element="Cryo", attack_type="Elemental Skill",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.wearer_sc_hit = models.Ability(
            "WearerSC", "WearerSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.tm_sc_probe = models.Ability(
            "TmSC", "TmSC", 1.0, element="Electro", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )

    def test_silver_light_stacks_and_heart_of_the_furnace_4pc(self):
        team = [self.wearer, self.teammate]

        # 1. Two Skill casts stack Silver Light R5 twice (+104 * 2 = +208 EM):
        #    Base ATK = 1000, ATK% = 41.3% (Silver Light) + 18% (Furnace 2pc) = 59.3% -> 1593.0 ATK
        #    2 Skill hits -> 2 * (1593.0 * 1.5 * 0.5 * 0.9) = 2150.55
        # 2. Wearer deals Stellar-Conduct DMG:
        #    - Triggers Furnace 4pc: +12% ATK (1713.0 ATK) & +50% Party SG Reaction DMG%
        #    - Wearer SC hit also gets +208 EM bonus: (6 * 208) / (208 + 2000) = 13/23
        #    - Teammate SC probe (0 EM): 1000.0 * 1.50 * 1.5 * 0.9 = 2025.0
        res = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.skill_cast),
            simulator.RotationStep(self.wearer, self.skill_cast),
            simulator.RotationStep(self.wearer, self.wearer_sc_hit),
            simulator.RotationStep(self.teammate, self.tm_sc_probe),
        ])
        em_bonus = (6.0 * 208.0) / (208.0 + 2000.0)
        wearer_sc_dmg = 1713.0 * (1.0 + 0.50 + em_bonus) * 1.5 * 0.9
        self.assertAlmostEqual(res["Odette_Test"], 2150.55 + wearer_sc_dmg, places=4)
        self.assertAlmostEqual(res["Teammate"], 2025.0, places=4)

    def test_heart_of_the_furnace_party_bonus_applies_to_teammates(self):
        # Teammate with 2pc Furnace (+18% ATK) receives the +50% party SG DMG% from Odette's 4pc Furnace
        teammate_2pc = entities.Character(
            "Teammate_2pc", "Electro", 0, 10000, 1000.0, 500, entities.Weapon("W", "Sword", 0),
            artifact_set=[build_heart_of_the_furnace(pieces=2)],
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        res = simulator.simulate_rotation([self.wearer, teammate_2pc], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.wearer_sc_hit),
            simulator.RotationStep(teammate_2pc, self.tm_sc_probe),
        ])
        expected_teammate = 1180.0 * 1.50 * 1.5 * 0.9
        self.assertAlmostEqual(res["Teammate_2pc"], expected_teammate, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)