import engine.models as models
import engine.entities as entities
import re
# --- Constants ---

base_reaction_coefficients = {
    "Lunar-Bloom": 1,
    "Lunar-Crystallize": 1.6,
    "Lunar-Charged": 3,
    "Stellar-Conduct": 2,
    "Stellar Swirl": 1
}

# --- Functions ---

def calculate_hit_damage(attacker: entities.Character, ability: models.Ability, enemy: entities.Enemy, active_buffs: list[models.BuffRule]):
    """
    Calculates the damage the inputted attack would deal.

    Args:
        attacker (entities.Character): The attacking character.
        ability (models.Ability): The ability used by the attacker.
        enemy (entities.Enemy): The enemy being attacked by the attacker.
        active_buffs (list[models.BuffRule]): The buffs currently active on the attacker.

    Returns:
        final_damage (float): The total damage dealt by the attack.
    """
    base_stats = attacker.out_of_combat_stats()

    for buff in active_buffs:
        if buff.element_filters:
            if not (ability.element in buff.element_filters):
                continue

        if buff.ability_filters:
            if not ((ability.attack_type in buff.ability_filters) or any(
                    tag in buff.ability_filters for tag in ability.tags)):
                continue

        base_stats[buff.stat] = base_stats.get(buff.stat, 0.0) + buff.base_value

    base_stats["HP"] = base_stats["Base HP"] * (1 + base_stats["HP%"]) + base_stats["Flat HP"]
    base_stats["ATK"] = base_stats["Base ATK"] * (1 + base_stats["ATK%"]) + base_stats["Flat ATK"]
    base_stats["DEF"] = base_stats["Base DEF"] * (1 + base_stats["DEF%"]) + base_stats["Flat DEF"]

    base_dmg = base_stats[ability.scaling_stat] * ability.mv
    base_dmg_mult = 1 + base_stats.get("Base DMG Mult", 0.0)
    effective_res = enemy.resistances.get(ability.element, 0.1) - base_stats.get("RES Shred", 0.0)

    if effective_res < 0:
        res_mult = 1 - effective_res / 2
    elif 0.75 > effective_res >= 0:
        res_mult = 1 - effective_res
    else:
        res_mult = 1 / (4 * effective_res + 1)

    crit_mult = 1 + max(0, min(1, base_stats["Crit Rate"])) * base_stats["Crit Damage"]

    if not (any(re.search(r"stellar|lunar", tag, re.IGNORECASE) for tag in ability.tags)):

        additive_base_dmg = base_stats.get("Flat DMG", 0.0)
        dmg_p_mult = 1 + base_stats.get("All DMG%", 0.0) + base_stats.get(f"{ability.element} DMG%", 0.0) + base_stats.get(f"{ability.attack_type} DMG%", 0.0)

        def_mult = (attacker.lvl + 100) / (attacker.lvl + 100 + ((enemy.lvl + 100) * (1 - base_stats.get("Def Shred", 0.0)) * (1 - base_stats.get("Def Ignore", 0.0))))
        reaction_mult = 1

        final_dmg = ((base_dmg * base_dmg_mult) + additive_base_dmg) * dmg_p_mult * crit_mult * def_mult * res_mult * reaction_mult



    else:
        base_reaction_coefficient = base_reaction_coefficients[ability.attack_type]
        reaction_base_dmg_p = 1 + base_stats.get("Reaction Base DMG%", 0.0)
        reaction_dmg_p = 1 + ((6 * base_stats.get("Elemental Mastery", 0.0)) / (base_stats.get("Elemental Mastery", 0.0) + 2000)) + base_stats.get(f"{ability.attack_type} DMG%", 0.0) + base_stats.get("Stellar DMG%", 0.0) + base_stats.get("Lunar DMG%", 0.0)
        additive_base_dmg = base_stats.get("Reaction Flat DMG", 0.0)
        elevation_mult = 1 + base_stats.get("Elevation%", 0.0)

        final_dmg = ((base_reaction_coefficient * base_dmg * base_dmg_mult * reaction_base_dmg_p * reaction_dmg_p) + additive_base_dmg) * elevation_mult * crit_mult * res_mult

    return final_dmg





