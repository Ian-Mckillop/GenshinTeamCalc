import engine.models as models

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


