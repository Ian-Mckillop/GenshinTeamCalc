import engine.models as models
import engine.entities as entities

"""
anaSkillTap = models.Ability(
    parent_name="Skill: Tap",
    component_name="Skill: Tap",
    mv=2.128
)



anaHoldSkill = models.StateRule(
    state_id= "ANA_HOLD_SKILL",
    base_duration= 15,
)

anaAccBase = models.BuffRule(
    buff_id= "BUFF_ANA_ACC_BASE",
    buff_name= "Accolades (Base)",
    stat= "Crit Damage",
    base_value= .12,
    character_source= "Anastasya",
    required_states= ["ANA_ACCOLADES"],
    buff_group= "GRP_ACCOLADES",

)



print(anaSkillTap)
print(anaHoldSkill)
print(anaAccBase)
"""

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
        "Crit Rate": .192
    },
    artifact_stats= models.artifact_stats(sands= "ATK%", gob= "ATK%", circ= "Crit Damage", em= 6,cr= 4,cd= 8,er= 2)

)

Anastasya.out_of_combat_stats()