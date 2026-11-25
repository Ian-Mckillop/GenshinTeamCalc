import engine.models as models
import engine.entities as entities
from engine.damage import calculate_hit_damage
from engine.simulator import simulate_rotation, RotationStep
"""

ana_palestar_hit_1 = models.Ability(
    parent_name="Skill: Palestar Crown",
    component_name="Skill: Palestar Crown Hit 1",
    mv=1.152,
    hit_index= 1,
    total_hits= 3,
    scaling_stat= "ATK",
    element= "Cryo",
    attack_type= "Skill",
    tags= [
        "TAG_SKILL",
        "TAG_SUMMON"
    ],
    hit_offsets=[2,4,6,8,10,12,14,16,18,20],
    summon_id= "Palestar Crown"
)

ana_palestar_hit_2 = models.Ability(
    parent_name="Skill: Palestar Crown",
    component_name="Skill: Palestar Crown Hit 2",
    mv=1.152,
    hit_index= 2,
    total_hits= 3,
    scaling_stat= "ATK",
    element= "Cryo",
    attack_type= "Skill",
    tags= [
        "TAG_SKILL",
        "TAG_SUMMON"
    ],
    hit_offsets=[2,4,6,8,10,12,14,16,18,20],
    summon_id= "Palestar Crown"
)

ana_palestar_hit_3 = models.Ability(
    parent_name="Skill: Palestar Crown",
    component_name="Skill: Palestar Crown Hit 3",
    mv=0,
    hit_index= 3,
    total_hits= 3,
    scaling_stat= "ATK",
    element= "Cryo",
    attack_type= "Skill",
    tags= [
        "TAG_SKILL",
        "TAG_SUMMON"
    ],
    hit_offsets=[2,4,6,8,10,12,14,16,18,20],
    summon_id= "Palestar Crown"
)

ana_skill_tap = models.Ability(
    parent_name="Skill: Tap",
    component_name="Skill: Tap",
    mv=2.128,
    total_hits= 1,
    scaling_stat= "ATK",
    element= "Cryo",
    attack_type= "Skill",
    tags= [
        "TAG_SKILL",
        "TAG_ANA_TAP_SKILL",
    ],
    cast_duration= 1,
    hit_offsets= [1],
    sub_abilities= [ana_palestar_hit_1, ana_palestar_hit_2, ana_palestar_hit_3]

)








state_ana_accolades = models.StateRule(
    state_id= "ANA_ACCOLADES",
    base_duration= 20,
    trigger_tags= [
        "TAG_ANA_TAP_SKILL",
        "CAST"
    ],
    termination_rules= ["FULL_DURATION"],
)

buff_ana_accolades_base = models.BuffRule(
    buff_id= "BUFF_ANA_ACC_BASE",
    buff_name= "Accolades (Base)",
    stat= "Crit Damage",
    base_value= .12,
    required_states= ["ANA_ACCOLADES"],
)






Silverdawn = entities.Weapon(
    name="Silverdawn",
    type= "Bow",
    base_atk= 674,
    secondary_stats= {
        "Crit Damage": 0.441
    },
)

Epochal_Advent = entities.ArtifactSet(
    name="Epochal Advent",
    two_piece_stats= {
        "ATK%": .18
    },
)

Anastasya = entities.Character(
    name="Anastasya",
    element= "Cryo",
    constellation= 0,
    base_hp= 12736,
    base_atk= 356,
    base_def= 779,
    weapon= Silverdawn,
    lvl= 90,
    artifact_set= [Epochal_Advent],
    ascension_stat= {
        "Crit Damage": .384
    },
    artifact_stats= models.artifact_stats(sands= "ATK%", gob= "ATK%", circ= "Crit Damage",cr= 10,cd= 8,er= 2),
    abilities= [ana_skill_tap],
    state_rules= [state_ana_accolades],
    buff_rules= [buff_ana_accolades_base],
    reaction_override= {
        "Superconduct" : "Stellar-Conduct",
        "Swirl" : "Stellar Swirl",
    },
    polestar_bonus_stacks= 1,
    polestar_instant_buff= True,
    instant_lv2_vortex= True,
)

test_enemy = entities.Enemy()

calculate_hit_damage(Anastasya, ana_skill_tap, test_enemy, [buff_ana_accolades_base])

first_step = RotationStep(Anastasya, ana_skill_tap)
rotation = simulate_rotation([Anastasya], test_enemy, [first_step])
print(rotation)

"""

print(len([1, None, None]))