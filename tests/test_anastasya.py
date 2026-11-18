import unittest

import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.characters.anastasya import build_anastasya


class TestAnastasyaC0(unittest.TestCase):
    def setUp(self):
        # 1000 Total Base ATK (330 + 670), 100% Crit Rate, 50% base Crit DMG (canceling 38.4% ascension)
        self.weapon = entities.Weapon("TestBow", "Bow", 670.0)
        self.ana, self.ab = build_anastasya(
            self.weapon,
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
        self.tm_hydro = entities.Character(
            "TM_Hydro", "Hydro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.team = [self.ana, self.tm_electro, self.tm_anemo, self.tm_hydro]
        self.probe = models.Ability("Probe", "Probe", 1.0, element="Physical", gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1)
        self.idle_6_5 = models.Ability("Idle", "Idle", 0.0, element="Physical", gauge_units=0.0, cast_duration=6.5)
        self.idle_45 = models.Ability("Idle", "Idle", 0.0, element="Physical", gauge_units=0.0, cast_duration=45.0)

    def test_accolades_love_burst_redistribution_and_triumph(self):
        # 1. Normal Accolades after Skill: 50% + 12% = 62% CD -> 1000 * 1.62 * 0.5 * 0.9 = 729.0
        res_normal = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.tm_electro, self.probe),
        ])
        self.assertAlmostEqual(res_normal["TM_Electro"], 729.0, places=4)

        # 2. Love Burst -> Swap out seals Anastasya for 6s:
        # 3 unsealed teammates split Anastasya's 12% -> 12% + 4% = 16% CD -> 1000 * 1.66 * 0.5 * 0.9 = 747.0
        # Casting Triumph early (while still sealed) deals 0 Triumph damage
        res_sealed = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Love"]),
            simulator.RotationStep(self.tm_electro, self.probe),
            simulator.RotationStep(self.ana, self.ab["Triumph"]),
        ])
        self.assertAlmostEqual(res_sealed["TM_Electro"], 747.0, places=4)

        # 3. After 6.5s (Seal ended, 8s post-seal sharing active):
        # All 4 characters are unsealed and split the 12% pool -> 12% + 3% = 15% CD -> 1000 * 1.65 * 0.5 * 0.9 = 742.5
        # Triumph is now unlocked and fires!
        res_post_seal = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Love"]),
            simulator.RotationStep(self.tm_electro, self.idle_6_5),
            simulator.RotationStep(self.tm_electro, self.probe),
            simulator.RotationStep(self.ana, self.ab["Triumph"]),
        ])
        self.assertAlmostEqual(res_post_seal["TM_Electro"], 742.5, places=4)
        self.assertAlmostEqual(res_post_seal["Anastasya"] - res_sealed["Anastasya"], 7676.9513, places=3)

    def test_accolades_honor_burst_and_doom(self):
        # Honor Burst seals 3 teammates -> Anastasya keeps her 12% + gets 3 * 12% = 48% CD (98% total -> 1.98x)
        res_sealed = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Honor"]),
            simulator.RotationStep(self.ana, self.probe),
            simulator.RotationStep(self.ana, self.ab["Doom"]),  # Too early -> 0 Doom damage
        ])
        expected_sealed = (
            1000.0 * 2.837 * 1.62 * 0.5 * 0.9         # Skill_Hold (Cryo Skill, 62% CD)
            + 1000.0 * 5.611 * 1.07 * 1.98 * 0.9       # Burst_Honor (Direct Stellar-Conduct, 98% CD)
            + 1000.0 * 1.0 * 1.98 * 0.5 * 0.9          # Physical Probe (98% CD)
        )
        self.assertAlmostEqual(res_sealed["Anastasya"], expected_sealed, places=4)

        # Wait 6.5s so teammates' Seal expires -> Doom unlocks and fires!
        res_doom = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Honor"]),
            simulator.RotationStep(self.ana, self.idle_6_5),
            simulator.RotationStep(self.ana, self.ab["Doom"]),
        ])
        self.assertGreater(res_doom["Anastasya"] - res_sealed["Anastasya"], 12000.0)

    def test_palestar_crown_freeze_and_extra_burst_hit(self):
        # Without Burst: Crown lasts 20s -> 9 ticks (t = 2, 4, ..., 18s)
        res_no_burst = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.ana, self.idle_45),
        ])
        # With Love Burst: Crown freezes for +20s (40s total -> 19 ticks) + adds 3rd hit per tick
        res_with_burst = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Tap"]),
            simulator.RotationStep(self.ana, self.ab["Burst_Love"]),
            simulator.RotationStep(self.ana, self.idle_45),
        ])
        self.assertGreater(res_with_burst["Anastasya"], res_no_burst["Anastasya"] * 2.0)

    def test_radiance_transformations_conduct_and_swirl(self):
        electro_hit = models.Ability("EHit", "EHit", 0.0, element="Electro", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE")
        anemo_hit = models.Ability("AHit", "AHit", 0.0, element="Anemo", gauge_units=1.0, hit_offsets=[0.0], cast_duration=0.1, icd_group="NONE")

        # 1. Baseline Spear_N1 (no Radiance -> 1.129 Cryo Normal Attack)
        res_normal = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N1"]),
        ])
        expected_normal = 1000.0 * (2.837 + 1.129) * 1.62 * 0.5 * 0.9
        self.assertAlmostEqual(res_normal["Anastasya"], expected_normal, places=4)

        # 2. Radiance: Stellar-Conduct (Polestar Field +29% Cryo DMG% & 1.45x Base Coeff, Spear_N1 -> 0.929 Direct SC)
        res_sc = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.tm_electro, electro_hit),
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.ana, self.ab["Spear_N1"]),
        ])
        expected_sc = (
            1000.0 * 2.837 * 1.29 * 1.62 * 0.5 * 0.9
            + 1000.0 * 0.929 * 1.45 * 1.07 * 1.62 * 0.9
        )
        self.assertAlmostEqual(res_sc["Anastasya"], expected_sc, places=4)

        # 3. Radiance: Stellar Swirl (A4 +15% & P3 +7% Base DMG%, Spear_N1 -> 1.393 Direct Stellar Swirl)
        res_ss = simulator.simulate_rotation(self.team, entities.Enemy(lvl=90), [
            simulator.RotationStep(self.ana, self.ab["Skill_Hold"]),
            simulator.RotationStep(self.tm_anemo, anemo_hit),
            simulator.RotationStep(self.ana, self.ab["Spear_N1"]),
        ])
        expected_ss = (
            1000.0 * 2.837 * 1.62 * 0.5 * 0.9
            + 1000.0 * 1.393 * 1.22 * 1.62 * 0.9
        )
        self.assertAlmostEqual(res_ss["Anastasya"], expected_ss, places=4)

class TestAnastasyaConstellations(unittest.TestCase):
    def setUp(self):
        self.weapon = entities.Weapon("TestBow", "Bow", 670.0)
        self.tm_cryo = entities.Character(
            "TM_Cryo", "Cryo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.tm_electro = entities.Character(
            "TM_Electro", "Electro", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.tm_anemo = entities.Character(
            "TM_Anemo", "Anemo", 0, 10000, 1000, 500, entities.Weapon("W", "Sword", 0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 0.0},
        )
        self.probe_phys = models.Ability("Probe", "Probe", 1.0, element="Physical", gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1)
        self.probe_sc = models.Ability("ProbeSC", "ProbeSC", 1.0, element="Cryo", attack_type="Stellar-Conduct", tags=["Stellar", "Stellar-Conduct"], gauge_units=0.0, hit_offsets=[0.0], cast_duration=0.1)

    def test_c1_and_c4_accolades_scaling(self):
        ana_c4, ab_c4 = build_anastasya(
            self.weapon, constellation=4, artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384}
        )
        team = [ana_c4, self.tm_cryo, self.tm_electro, self.tm_anemo]

        # At C4 while Anastasya is Sealed:
        # TM_Cryo gets own Accolades (15.6% CD + 19.5% ATK) + 300%/3 of Anastasya's Accolades (15.6% CD + 19.5% ATK)
        # Total = 1390 ATK, 31.2% CD (1.812x) -> 1390 * 1.812 * 0.5 * 0.9 = 1133.406
        res = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c4, ab_c4["Skill_Tap"]),
            simulator.RotationStep(ana_c4, ab_c4["Burst_Love"]),
            simulator.RotationStep(self.tm_cryo, self.probe_phys),
        ])
        self.assertAlmostEqual(res["TM_Cryo"], 1133.406, places=4)

    def test_c2_love_and_honor_buffs(self):
        ana_c2, ab_c2 = build_anastasya(
            self.weapon, constellation=2, artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384}
        )
        team = [ana_c2, self.tm_cryo, self.tm_electro, self.tm_anemo]

        # C2 Love: +60% Stellar Glimmer Crit DMG on top of Accolades (12% + 15% ATK -> 1150 ATK, 122% CD -> 2.22x)
        res_love = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c2, ab_c2["Skill_Tap"]),
            simulator.RotationStep(self.tm_cryo, self.probe_sc),
        ])
        # C2 Love: +60% Stellar Glimmer Crit DMG + Accolades (12% CD, 15% ATK -> 1150 ATK) + P3 (+8.05% Reaction Base DMG%)
        expected_tm_cryo = 1150.0 * 1.0 * (1 + 0.00007 * 1150.0) * 2.22 * 0.9
        self.assertAlmostEqual(res_love["TM_Cryo"], expected_tm_cryo, places=4)

        # C2 Honor: 1.25x Original DMG Mult on Spear_N1 + 5% Stellar Glimmer Elevation
        res_honor = simulator.simulate_rotation(team, entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c2, ab_c2["Skill_Hold"]),
            simulator.RotationStep(ana_c2, ab_c2["Spear_N1"]),
        ])
        expected_ana = 1150.0 * (2.837 + 1.129 * 1.25) * 1.62 * 0.5 * 0.9
        self.assertAlmostEqual(res_honor["Anastasya"], expected_ana, places=4)

    def test_c6_auto_triumph_and_doom(self):
        ana_c5, ab_c5 = build_anastasya(
            self.weapon, constellation=5, artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384}
        )
        ana_c6, ab_c6 = build_anastasya(
            self.weapon, constellation=6, artifact_stats={"Crit Rate": 0.95, "Crit Damage": -0.384}
        )

        # C6 Love: swapping out triggers 250% Triumph + 10% Elevation
        res_c5_love = simulator.simulate_rotation([ana_c5, self.tm_cryo, self.tm_electro, self.tm_anemo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c5, ab_c5["Skill_Tap"]),
            simulator.RotationStep(self.tm_cryo, self.probe_sc),
        ])
        res_c6_love = simulator.simulate_rotation([ana_c6, self.tm_cryo, self.tm_electro, self.tm_anemo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c6, ab_c6["Skill_Tap"]),
            simulator.RotationStep(self.tm_cryo, self.probe_sc),
        ])
        self.assertGreater(res_c6_love["Anastasya"] - res_c5_love["Anastasya"], 25000.0)
        self.assertAlmostEqual(res_c6_love["TM_Cryo"] / res_c5_love["TM_Cryo"], 1.10, places=4)

        # C6 Honor: tapping Skill after Hold Skill triggers 200% Doom 3-Hit with full party Accolades + 20% Elevation
        res_c5_honor = simulator.simulate_rotation([ana_c5, self.tm_cryo, self.tm_electro, self.tm_anemo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c5, ab_c5["Skill_Hold"]),
            simulator.RotationStep(ana_c5, ab_c5["Skill_Tap"]),
        ])
        res_c6_honor = simulator.simulate_rotation([ana_c6, self.tm_cryo, self.tm_electro, self.tm_anemo], entities.Enemy(lvl=90), [
            simulator.RotationStep(ana_c6, ab_c6["Skill_Hold"]),
            simulator.RotationStep(ana_c6, ab_c6["Skill_Tap"]),
        ])
        self.assertGreater(res_c6_honor["Anastasya"] - res_c5_honor["Anastasya"], 25000.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)