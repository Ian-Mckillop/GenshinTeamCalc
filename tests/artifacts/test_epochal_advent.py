import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.artifacts.epochal_advent import build_epochal_advent


class TestEpochalAdvent(unittest.TestCase):
    def setUp(self):
        # Wearer: 1000 Base ATK, 5% base CR + 55% artifact CR = 60% base CR, 50% total CD (1.5x)
        # 2pc Epochal Advent grants +18% ATK -> 1180.0 Total ATK
        self.epochal_4pc = build_epochal_advent(pieces=4)
        self.wearer = entities.Character(
            "Anastasya_Test", "Cryo", 0, 10000.0, 1000.0, 500.0,
            entities.Weapon("W", "Bow", 0.0),
            weapon_type="Bow",
            artifact_set=[self.epochal_4pc],
            artifact_stats={"Crit Rate": 0.55, "Crit Damage": 0.0},
        )
        self.teammate = entities.Character(
            "Teammate", "Electro", 0, 10000.0, 1000.0, 500.0,
            entities.Weapon("W", "Sword", 0.0),
        )
        self.phys_na = models.Ability(
            "PhysNA", "PhysNA", 1.0, element="Physical", attack_type="Normal Attack",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.cryo_skill = models.Ability(
            "CryoSkill", "CryoSkill", 1.0, element="Cryo", attack_type="Elemental Skill",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.cryo_burst = models.Ability(
            "CryoBurst", "CryoBurst", 1.0, element="Cryo", attack_type="Elemental Burst",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.cryo_sc_hit = models.Ability(
            "CryoSC", "CryoSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )
        self.cryo_probe = models.Ability(
            "CryoProbe", "CryoProbe", 1.0, element="Cryo", attack_type="Charged Attack",
            gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1,
        )

    def test_undying_radiance_crit_rate_bonuses(self):
        # 1. Physical NA grants 1 Starspark, but Physical DMG gets 0% CR bonus (stays at 60% CR -> 1.30x):
        #    1180.0 * 1.30 * 0.5 * 0.9 = 690.3
        # 2. Cryo Skill gets +20% CR (80% CR -> 1.40x):
        #    1180.0 * 1.40 * 0.5 * 0.9 = 743.4
        # 3. Cryo Stellar-Conduct hit gets +20% + 20% = +40% CR (100% CR -> 1.50x, ignores DEF):
        #    1180.0 * 1.50 * 0.9 = 1593.0
        res = simulator.simulate_rotation([self.wearer], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.phys_na),
            simulator.RotationStep(self.wearer, self.cryo_skill),
            simulator.RotationStep(self.wearer, self.cryo_sc_hit),
        ])
        self.assertAlmostEqual(res["Anastasya_Test"], 690.3 + 743.4 + 1593.0, places=4)

    def test_starspark_cap_and_3s_sequential_decay(self):
        # Skill (t=0.0s -> stack 1 expires 3.0s) + Burst (t=0.1s -> stack 2 expires 6.0s) + NA (t=0.2s -> capped at 2)
        # - After 3.0s idle (t=3.3s): 1st stack expired, 2nd stack still active -> Cryo probe gets +20% CR (743.4)
        # - After 3.0s more idle (t=6.4s): 2nd stack expired -> Undying Radiance ends -> Cryo probe at 60% CR (690.3)
        idle_3 = models.Ability(
            "Idle3", "Idle3", 0.0, element="Physical", attack_type="Idle",
            gauge_units=0.0, cast_duration=3.0,
        )
        res = simulator.simulate_rotation([self.wearer], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.cryo_skill),
            simulator.RotationStep(self.wearer, self.cryo_burst),
            simulator.RotationStep(self.wearer, self.phys_na),
            simulator.RotationStep(self.wearer, idle_3),
            simulator.RotationStep(self.wearer, self.cryo_probe),
            simulator.RotationStep(self.wearer, idle_3),
            simulator.RotationStep(self.wearer, self.cryo_probe),
        ])
        expected = 743.4 + 743.4 + 690.3 + 743.4 + 690.3
        self.assertAlmostEqual(res["Anastasya_Test"], expected, places=4)

    def test_starspark_pauses_while_off_field(self):
        # Gain 1 Starspark at t=0.0s (3.0s timer), swap to Teammate for 5.0s, then swap back to Wearer:
        # Because Starspark only decays while on-field, Wearer still holds Starspark upon swapping back!
        idle_5 = models.Ability("Idle5", "Idle5", 0.0, element="Physical", gauge_units=0.0, cast_duration=5.0)
        res = simulator.simulate_rotation([self.wearer, self.teammate], entities.Enemy(lvl=90), [
            simulator.RotationStep(self.wearer, self.cryo_skill),
            simulator.RotationStep(self.teammate, idle_5),
            simulator.RotationStep(self.wearer, self.cryo_probe),
        ])
        self.assertAlmostEqual(res["Anastasya_Test"], 743.4 + 743.4, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)