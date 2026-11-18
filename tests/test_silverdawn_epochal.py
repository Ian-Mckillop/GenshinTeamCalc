import unittest
import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.characters.anastasya import build_anastasya
from data.weapons.silverdawn import build_silverdawn
from data.artifacts.epochal_advent import build_epochal_advent


class TestSilverdawnAndEpochalAdvent(unittest.TestCase):
    def setUp(self):
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0)
        )
        self.tm_anemo = entities.Character(
            "TM_Anemo", "Anemo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0)
        )
        self.tm_hydro = entities.Character(
            "TM_Hydro", "Hydro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0)
        )

    def test_silverdawn_extension_and_buffs(self):
        # 330 + 674 = 1004 Base ATK; 50% + 38.4% + 44.1% = 132.5% base Crit DMG
        # Active buffs: +40% ATK (Silverdawn) + 18% ATK (2pc Epochal) = 1586.32 ATK
        # Stellar Glimmer Crit DMG: 132.5% + 12% (Accolades) + 40% (Silverdawn) = 184.5% (2.845x)
        # Cryo Stellar Glimmer Crit Rate: 5% + 55% + 40% (4pc Epochal) = 100%
        ana, ab = build_anastasya(
            build_silverdawn(),
            artifact_set=[build_epochal_advent()],
            artifact_stats={"Crit Rate": 0.55},
        )
        team = [ana, self.tm_electro, self.tm_anemo, self.tm_hydro]

        # Off-field hit at t=4.0s extends White Crown's Bequest from 6.0s -> 9.0s, so hit at t=8.0s still gets the buff!
        late_sc = models.Ability(
            "LateSC", "LateSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[3.5, 7.5], cast_duration=0.0
        )
        wait_tm = models.Ability("Wait", "Wait", 0.0, element="Electro", gauge_units=0.0, cast_duration=8.0)

        res = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(ana, ab["Skill_Hold"]), # t=0.0, hit at 0.25 (ATK = 1586.32, Cryo CR = 80%, CD = 144.5%)
            simulator.RotationStep(ana, late_sc),          # t=0.65 -> hits at 4.15s & 8.15s
            simulator.RotationStep(self.tm_electro, wait_tm),
        ])

        expected_hold = 1586.32 * 2.837 * (1 + 0.80 * 1.445) * 0.5 * 0.9
        expected_late_sc = 1586.32 * 1.0 * (1 + 0.00007 * 1586.32) * 2.845 * 0.9
        self.assertAlmostEqual(res["Anastasya"], expected_hold + 2 * expected_late_sc, places=3)

    def test_epochal_advent_on_field_decay_vs_off_field_persistence(self):
        ana, ab = build_anastasya(
            entities.Weapon("FlatBow", "Bow", 670.0), # 1000 Base ATK
            artifact_set=[build_epochal_advent()],
            artifact_stats={"Crit Rate": 0.55, "Crit Damage": -0.384}, # 60% base CR -> 100% on Stellar with Starspark, 60% without
        )
        team = [ana, self.tm_electro, self.tm_anemo, self.tm_hydro]

        # Stay on-field for 7s with 1 Starspark (from Skill_Hold at t=0.0 -> expires at t=3.0s)
        idle_ana = models.Ability("Idle", "Idle", 0.0, element="Cryo", gauge_units=0.0, cast_duration=6.5)
        probe_sc = models.Ability(
            "ProbeSC", "ProbeSC", 1.0, element="Cryo", attack_type="Stellar-Conduct",
            tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1
        )

        res_expired = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(ana, ab["Skill_Hold"]), # +1 Starspark at t=0.0, decays at t=3.0
            simulator.RotationStep(ana, idle_ana),         # waits until t=7.15s on-field
            simulator.RotationStep(ana, probe_sc),         # Starspark is gone -> 60% CR instead of 100% CR
        ])

        # 1000 * (1 + 0.18) = 1180 ATK; CD = 50% + 12% = 62%
        expected_hold = 1180.0 * 2.837 * (1 + 0.80 * 0.62) * 0.5 * 0.9
        expected_probe_no_sp = 1180.0 * 1.0 * (1 + 0.00007 * 1180.0) * (1 + 0.60 * 0.62) * 0.9
        self.assertAlmostEqual(res_expired["Anastasya"], expected_hold + expected_probe_no_sp, places=3)


if __name__ == "__main__":
    unittest.main()