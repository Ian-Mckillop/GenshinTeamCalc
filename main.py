import engine.models as models
import engine.entities as entities
import engine.damage as damage
from engine.damage import calculate_hit_damage


ana_skill_tap = models.Ability(
    parent_name="Skill: Tap",
    component_name="Skill: Tap",
    mv=2.128,
    total_hits= 1,
    scaling_stat= "ATK",
    element= "Cryo",
    attack_type= "Stellar-Conduct",
    tags= [
        "TAG_SKILL",
        "TAG_ANA_TAP_SKILL",
        "TAG_STELLAR_CONDUCT"
    ]
)



anaHoldSkill = models.StateRule(
    state_id= "ANA_HOLD_SKILL",
    base_duration= 15,
)

ana_acc_base = models.BuffRule(
    buff_id= "BUFF_ANA_ACC_BASE",
    buff_name= "Accolades (Base)",
    stat= "Crit Damage",
    base_value= .12,
    character_source= "Anastasya",
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
        "Crit Rate": .192
    },
    artifact_stats= models.artifact_stats(sands= "ATK%", gob= "ATK%", circ= "Crit Damage", em= 6,cr= 4,cd= 8,er= 2)

)

test_enemy = entities.Enemy()

calculate_hit_damage(Anastasya, ana_skill_tap, test_enemy, [ana_acc_base])