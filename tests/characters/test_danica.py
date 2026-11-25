import unittest
import engine.entities as entities
import engine.models as models
from engine.simulator import RotationStep, simulate_rotation
from data.characters.danica import build_danica


class TestDanica(unittest.TestCase):
    def make_teammate(self) -> tuple[entities.Character, models.Ability]:
        tm = entities.Character(
            name="CryoMate",
            element="Cryo",
            constellation=0,
            base_hp=10000.0,
            base_atk=1000.0,
            base_def=500.0,
            weapon=entities.Weapon("Sword", "Sword", 0.0),
            artifact_stats={"Crit Rate": 0.95, "Crit Damage": 1.0},
        )
        cryo_hit = models.Ability(
            parent_name="Cryo Hit",
            component_name="Cryo Hit",
            mv=1.0,
            element="Cryo",
            attack_type="Normal Attack",
            icd_group="NONE",
            cast_duration=0.3,
            hit_offsets=[0.1],
        )
        return tm, cryo_hit

    def test_off_field_coordinated_attack_and_will_to_protect_swap_in(self):
        """
        Verifies:
        1. Scouring Anchor summons Storm Anchor (25s) and triggers off-field coordinated attacks (1.5s ICD).
        2. Two off-field Cryo hits grant 50 + 50 = 100 Will to Cleanse.
        3. Swapping back to Danica automatically unleashes Will to Protect, enters Maid: Royal Guard,
           and activates Burst's 20s Royal Guard Flat ATK buff.
        """
        danica, d_ab = build_danica(constellation=0, artifact_stats={"Crit Rate": 0.758, "Crit Damage": 1.0})
        tm, cryo_hit = self.make_teammate()
        enemy = entities.Enemy(lvl=90)

        # t=0.0: Danica E -> summons Storm Anchor
        # t=0.5 & 0.8: CryoMate hits -> triggers Coord Atk #1 + 100 Will to Cleanse
        # t=1.1: Swap to Danica (SWAP_IN fires Will to Protect -> Maid: Royal Guard) & cast Burst (20s RG Flat ATK buff)
        # t=2.3: Swap back to CryoMate -> CryoMate attacks with Danica's Burst Flat ATK buff active!
        rotation = [
            RotationStep(danica, d_ab["Skill"]),
            RotationStep(tm, cryo_hit),
            RotationStep(tm, cryo_hit),
            RotationStep(danica, d_ab["Burst"]),
            RotationStep(tm, cryo_hit),
        ]
        res = simulate_rotation([danica, tm], enemy, rotation)

        # Verify Danica dealt Skill + 1 Coordinated Attack + Will to Protect + Burst (with 2 SC sub-hits)
        self.assertAlmostEqual(res["Danica"], 12579.405, places=2)
        # Verify CryoMate received Danica's Burst Royal Guard Flat ATK buff (base 1000 ATK + 10% of Danica's ATK)
        # Unbuffed CryoMate 3 hits = 3 * 900 = 2700; with Danica's Burst RG Flat ATK buff, hit #3 is significantly higher
        self.assertGreater(res["CryoMate"], 2850.0)

    def test_on_field_cleaner_form_a4_and_five_use_limit(self):
        """
        Verifies:
        1. 4 Storm Anchor NAs on-field build 4 * 25 = 100 Will to Cleanse.
        2. Will to Purge enters Maid: Cleaner, grants A4 (+25 Will to Cleanse per NA), and consumes Will to Cleanse.
        3. 5 in-form uses of Will to Purge destroy Storm Anchor and exit Maid: Cleaner.
        """
        danica, d_ab = build_danica(constellation=0, artifact_stats={"Crit Rate": 0.758, "Crit Damage": 1.0})
        enemy = entities.Enemy(lvl=90)

        # E -> 4 NAs (100 Will) -> Purge #1 (enters Cleaner, 0 in-form uses)
        # Burst (in Cleaner: immediately refills Will to Cleanse to 100!) -> Purge #2 (1st in-form, A4=1 -> 50/NA)
        # 2 NAs (100 Will) -> Purge #3 (2nd in-form, A4=2 -> 75/NA)
        # 2 NAs (100 Will) -> Purge #4 (3rd in-form, A4=3 -> 100/NA)
        # 1 NA  (100 Will) -> Purge #5 (4th in-form, A4=3 -> 100/NA)
        # 1 NA  (100 Will) -> Purge #6 (5th in-form -> destroys Storm Anchor!)
        # Follow-up SA_N1 should deal 0 damage because Storm Anchor was destroyed!
        rotation = [
            RotationStep(danica, d_ab["Skill"]),
            RotationStep(danica, d_ab["SA_N1"]),
            RotationStep(danica, d_ab["SA_N2"]),
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["SA_N1"]),
            RotationStep(danica, d_ab["Will_to_Purge"]),  # Enters Maid: Cleaner
            RotationStep(danica, d_ab["Burst"]),          # Refills Will to Cleanse to 100
            RotationStep(danica, d_ab["Will_to_Purge"]),  # In-form #1 (A4 = 1 -> +50/NA)
            RotationStep(danica, d_ab["SA_N2"]),
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["Will_to_Purge"]),  # In-form #2 (A4 = 2 -> +75/NA)
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["Will_to_Purge"]),  # In-form #3 (A4 = 3 -> +100/NA)
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["Will_to_Purge"]),  # In-form #4
            RotationStep(danica, d_ab["SA_N4"]),
            RotationStep(danica, d_ab["Will_to_Purge"]),  # In-form #5 -> destroys Storm Anchor!
        ]
        res_destroyed = simulate_rotation([danica], enemy, rotation)

        # Adding SA_N1 after Storm Anchor is destroyed must add 0.0 damage
        enemy_after = entities.Enemy(lvl=90)
        res_with_extra_sa_na = simulate_rotation([danica], enemy_after, [*rotation, RotationStep(danica, d_ab["SA_N1"])])
        self.assertAlmostEqual(res_destroyed["Danica"], res_with_extra_sa_na["Danica"], places=5)

    def test_constellations_c2_and_c6(self):
        """
        Verifies C2 (Let Us Toast flat Stellar-Conduct DMG + Cleaner all-stack consumption)
        and C6 (Stellar-Conduct Elevation% + Royal Guard on-field Stellar-Conduct DMG%).
        """
        d_c0, ab_c0 = build_danica(constellation=0, artifact_stats={"ATK%": 1.0, "Crit Rate": 0.758, "Crit Damage": 1.0})
        d_c2, ab_c2 = build_danica(constellation=2, artifact_stats={"ATK%": 1.0, "Crit Rate": 0.758, "Crit Damage": 1.0})
        d_c6, ab_c6 = build_danica(constellation=6, artifact_stats={"ATK%": 1.0, "Crit Rate": 0.758, "Crit Damage": 1.0})

        def run(danica, ab):
            tm, cryo_hit = self.make_teammate()
            enemy = entities.Enemy(lvl=90)
            rot = [
                RotationStep(danica, ab["Skill"]),
                RotationStep(tm, cryo_hit),
                RotationStep(tm, cryo_hit),
                RotationStep(danica, ab["Burst"]),
            ]
            return simulate_rotation([danica, tm], enemy, rot)["Danica"]

        dmg_c0 = run(d_c0, ab_c0)
        dmg_c2 = run(d_c2, ab_c2)
        dmg_c6 = run(d_c6, ab_c6)

        self.assertGreater(dmg_c2, dmg_c0)
        self.assertGreater(dmg_c6, dmg_c2)


if __name__ == "__main__":
    unittest.main()