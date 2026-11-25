import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.artifacts.disenchantment_in_deep_shadow import build_disenchantment_in_deep_shadow
from data.weapons.echoes_of_the_heart import build_echoes_of_the_heart


class TestEchoesOfTheHeartAndDisenchantment(unittest.TestCase):
    def setUp(self):
        # Wearer with 435 Base ATK + 565 Echoes of the Heart = 1000 Base ATK
        # Base CR 5% + 79% artifact + 16% Disenchantment 4pc = 100% Crit Rate when Conduct-affected
        self.weapon_r1 = build_echoes_of_the_heart(refinement=1)
        self.disenchantment_4pc = build_disenchantment_in_deep_shadow(pieces=4)
        self.wearer = entities.Character(
            "Yae_Test", "Electro", 0, 10000, 435.0, 500, self.weapon_r1,
            weapon_type="Catalyst",
            artifact_set=[self.disenchantment_4pc],
            artifact_stats={"Crit Rate": 0.79, "Crit Damage": 0.0},
        )
        self.tm_cryo = entities.Character(
            "TM_Cryo", "Cryo", 0, 10000, 1000.0, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
            reaction_override={"Superconduct": "Stellar-Conduct"},
        )
        self.cryo_hit = models.Ability(
            "CHit", "CHit", 0.0, element="Cryo", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE",
        )
        self.electro_skill = models.Ability(
            "ESkill", "ESkill", 1.0, element="Electro", attack_type="Elemental Skill",
            gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE",
        )
        self.wearer_sc_hit = models.Ability(
            "WearerSC", "WearerSC", 1.0, element="Electro", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )

    def test_r1_echoes_and_disenchantment_4pc(self):
        # Total ATK = 1000 * (1 + 0.276 + 0.18) = 1456.0
        # 1. Electro Skill triggers Stellar-Conduct -> activates:
        #    - Disenchantment +16% CR (reaches 100% CR on this hit!)
        #    - Echoes of the Heart R1: +60 EM & +16% Stellar Glimmer Reaction DMG%
        #    - Hit 1 dmg = 1456.0 * 1.5 * 0.5 * 0.9 = 982.8
        # 2. Wearer Stellar-Conduct hit gets +16% (Echoes) + 40% (Disenchantment) = +56% Reaction DMG%
        #    plus +60 EM bonus = (6 * 60) / (60 + 2000)
        res = simulator.simulate_rotation([self.wearer, self.tm_cryo], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_cryo, self.cryo_hit),
            simulator.RotationStep(self.wearer, self.electro_skill),
            simulator.RotationStep(self.wearer, self.wearer_sc_hit),
        ])
        em_bonus = (6.0 * 60.0) / (60.0 + 2000.0)
        expected = 982.8 + 1456.0 * (1.0 + 0.56 + em_bonus) * 1.5 * 0.9
        self.assertAlmostEqual(res["Yae_Test"], expected, places=4)

    def test_r5_echoes_scaling(self):
        wearer_r5 = entities.Character(
            "Yae_R5", "Electro", 0, 10000, 435.0, 500, build_echoes_of_the_heart(refinement=5),
            weapon_type="Catalyst",
            artifact_set=[build_disenchantment_in_deep_shadow(pieces=4)],
            artifact_stats={"Crit Rate": 0.79, "Crit Damage": 0.0},
        )
        res = simulator.simulate_rotation([wearer_r5, self.tm_cryo], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_cryo, self.cryo_hit),
            simulator.RotationStep(wearer_r5, self.electro_skill),
            simulator.RotationStep(wearer_r5, self.wearer_sc_hit),
        ])
        em_bonus_r5 = (6.0 * 120.0) / (120.0 + 2000.0)
        expected_r5 = 982.8 + 1456.0 * (1.0 + 0.32 + 0.40 + em_bonus_r5) * 1.5 * 0.9
        self.assertAlmostEqual(res["Yae_R5"], expected_r5, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)