import engine.entities as entities
import engine.models as models
import engine.simulator as simulator
from data.artifacts.disenchantment_in_deep_shadow import build_disenchantment_in_deep_shadow
from data.artifacts.epochal_advent import build_epochal_advent
from data.artifacts.heart_of_the_furnace import build_heart_of_the_furnace
from data.artifacts.tenacity_of_the_millelith import build_tenacity_of_the_millelith
from data.characters.anastasya import build_anastasya
from data.characters.danica import build_danica
from data.characters.odette import build_odette
from data.characters.yae_miko import build_yae_miko
from data.weapons.echoes_of_the_heart import build_echoes_of_the_heart
from data.weapons.silver_light import build_silver_light
from data.weapons.silverdawn import build_silverdawn
from data.weapons.torrents_of_spring import build_torrents_of_spring
from data.weapons.ultimate_overlords_mega_magic_sword import  build_ultimate_overlords_mega_magic_sword
from data.weapons.jade_vista import build_jade_vista


def build_team():
    # =========================================================================
    # PLACEHOLDER ARTIFACT STATS (Main Stats + Substats)
    # Valid stat keys: "HP", "HP%", "ATK", "ATK%", "DEF", "DEF%",
    # "Elemental Mastery", "Crit Rate", "Crit Damage", "Energy Recharge%",
    # "Cryo DMG%", "Electro DMG%", "Physical DMG%", "Healing Bonus%"
    # =========================================================================
    anastasya_artifacts = models.artifact_stats("ATK%", "ATK%", "Crit Rate", cr=10, cd=8, er=2)
    odette_artifacts = models.artifact_stats("ATK%", "ATK%", "Crit Rate", atk_p=2, cr=8, cd=10)
    yae_artifacts = models.artifact_stats("ATK%", "ATK%", "Crit Damage", atk_p=2, cr=10, cd=8)
    danica_artifacts = models.artifact_stats("ATK%", "ATK%", "ATK%", atk_p=4, flat_atk=8, cr=8)

    # Build Characters & Loadouts
    anastasya, ana_ab = build_anastasya(
        constellation=6,
        weapon=build_silverdawn(refinement=1),
        artifact_set=[build_disenchantment_in_deep_shadow(),],
        artifact_stats=anastasya_artifacts,
    )
    odette, ode_ab = build_odette(
        constellation=0,
        weapon=build_silver_light(refinement=5),
        artifact_set=[build_heart_of_the_furnace(pieces=4)],
        artifact_stats=odette_artifacts,
    )
    yae, yae_ab = build_yae_miko(
        constellation=1,
        weapon=build_echoes_of_the_heart(refinement=5),
        artifact_set=[build_disenchantment_in_deep_shadow(pieces=4)],
        artifact_stats=yae_artifacts,
    )
    danica, dan_ab = build_danica(
        constellation=0,
        weapon=build_torrents_of_spring(refinement=1),
        artifact_set=[build_tenacity_of_the_millelith(pieces=4)],
        artifact_stats=danica_artifacts,
    )

    team = [danica, odette, yae, anastasya]
    abilities = {
        "Danica": dan_ab,
        "Odette": ode_ab,
        "Yae": yae_ab,
        "Anastasya": ana_ab,
    }
    return team, abilities


def build_rotation_steps(
    team: list[entities.Character],
    ab: dict[str, dict[str, models.Ability]],
    is_first_rotation: bool = False,
    is_second_rotation: bool = False,
    is_third_rotation: bool = False,
    swap_delay: float = 0.1000,
) -> list[simulator.RotationStep]:
    """
    Models: Danica (E) > Odette EE > Yae EEE > Danica Q > Anastasya hEQ 2N3D 2N3E 2N3D N2
    """
    danica, odette, yae, anastasya = team
    dan_ab = ab["Danica"]
    ode_ab = ab["Odette"]
    yae_ab = ab["Yae"]
    ana_ab = ab["Anastasya"]

    dash_cancel = models.Ability(
        parent_name="Dash",
        component_name="Dash Cancel",
        mv=0.0,
        element="Physical",
        attack_type="Dash",
        gauge_units=0.0,
        cast_duration=0.25,
    )

    steps: list[simulator.RotationStep] = []

    # 0. Danica: (E) [E is only cast on Rotation 1 before her anchor is up]
    if is_first_rotation:
        steps.append(simulator.RotationStep(danica, dan_ab["Skill"], swap_delay=swap_delay))

    # 1. Odette: EE
    steps.extend([
        simulator.RotationStep(odette, ode_ab["Skill"], swap_delay=swap_delay),
        simulator.RotationStep(odette, ode_ab["Skill_Coda"], swap_delay=swap_delay),
    ])

    # 2. Yae Miko: EEE
    steps.extend([
        simulator.RotationStep(yae, yae_ab["Skill_1"], swap_delay=swap_delay),
        simulator.RotationStep(yae, yae_ab["Skill_2"], swap_delay=swap_delay),
        simulator.RotationStep(yae, yae_ab["Skill_3"], swap_delay=swap_delay),
    ])

    # 3. Danica: Q
    steps.append(simulator.RotationStep(danica, dan_ab["Will_to_Protect"], swap_delay=swap_delay))
    steps.append(simulator.RotationStep(danica, dan_ab["Burst"], swap_delay=swap_delay))

    # 4. Anastasya: hEQ 2N3D 2N3E 2N3D N2

    steps.extend([
        simulator.RotationStep(anastasya, ana_ab["Skill_Hold"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Burst_Honor"], swap_delay=swap_delay),

        simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, dash_cancel, swap_delay=swap_delay),

        simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, dash_cancel, swap_delay=swap_delay),

        simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Doom_C6"], swap_delay=swap_delay),

        simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Doom_1"], swap_delay=swap_delay),

        simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        simulator.RotationStep(anastasya, ana_ab["Doom_2"], swap_delay=swap_delay),


        # simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        # simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
        # simulator.RotationStep(anastasya, ana_ab["Spear_N3"], swap_delay=swap_delay),
        # simulator.RotationStep(anastasya, dash_cancel, swap_delay=swap_delay),

        # simulator.RotationStep(anastasya, ana_ab["Spear_N1"], swap_delay=swap_delay),
        # simulator.RotationStep(anastasya, ana_ab["Spear_N2"], swap_delay=swap_delay),
    ])

    return steps


def compute_rotation_time(steps: list[simulator.RotationStep]) -> float:
    """
    Calculates total elapsed rotation time (cast durations + character swap delays).
    """
    total_time = 0.0
    active_char = None
    for step in steps:
        if active_char is not None and step.character.name != active_char.name:
            total_time += step.swap_delay
        active_char = step.character
        total_time += step.ability.cast_duration
    return total_time


def run():
    team, ab = build_team()
    enemy = entities.Enemy(lvl=100)

    # Chain 3 consecutive rotations in a single continuous simulation:
    # Rotation 1 (Danica E Q) + Rotation 2 (Danica Q) + Rotation 3 (Danica Q)
    all_steps: list[simulator.RotationStep] = []
    for rot_idx in range(3):
        all_steps.extend(
            build_rotation_steps(
                team,
                ab,
                is_first_rotation=(rot_idx == 0),
            )
        )

    rot_1_steps: list[simulator.RotationStep] = build_rotation_steps(
                team,
                ab,
                is_first_rotation=True,
            )
    rot_2_steps: list[simulator.RotationStep] = build_rotation_steps(
                team,
                ab,
                is_second_rotation=True,
            )
    rot_3_steps: list[simulator.RotationStep] = build_rotation_steps(
                team,
                ab,
                is_third_rotation=True,
            )

    rot_times = {
        1: compute_rotation_time(rot_1_steps),
        2: compute_rotation_time(rot_2_steps),
        3: compute_rotation_time(rot_3_steps),
    }
    total_time = compute_rotation_time(all_steps)
    results = simulator.simulate_rotation(team, enemy, all_steps, total_time, rot_times[1], rot_times[2])

    for rot in [1,2,3]:
        rot_time = rot_times[rot]
        total_dmg = sum(results[rot - 1].values())
        team_dps = total_dmg / rot_time if rot_time > 0 else 0.0

        print(f"=== Rotation #{rot} ===")
        print(f"Total Duration                 : {rot_time:.2f}")
        print(f"Total Team Damage              : {total_dmg:,.2f}")
        print(f"Team DPS Per Rot.              : {team_dps:,.2f}")
        for name, dmg in results[rot - 1].items():
            share = (dmg / total_dmg * 100.0) if total_dmg > 0 else 0.0
            char_dps = dmg / rot_time if rot_time > 0 else 0.0
            print(f"  {name:<12}: {dmg:>12,.2f} ({share:5.1f}%) | {char_dps:>9,.2f} DPS")
        print("\n")

if __name__ == "__main__":
    run()
