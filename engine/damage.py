import engine.models as models
import engine.entities as entities
import re
# --- Constants ---

base_reaction_coefficients = {
    "Lunar-Bloom": 1.0,
    "Lunar-Crystallize": 1.6,
    "Lunar-Charged": 3.0,
    "Stellar-Conduct": 1.0,
    "Stellar Swirl": 1.0
}

amplifying_coefficients = {
    "Melt": 2.0,
    "Vaporize": 2.0,
    "Reverse Melt": 1.5,
    "Reverse Vaporize": 1.5
}

additive_coefficients = {
    "Aggravate": 1.15,
    "Spread": 1.25
}

transformative_coefficients = {
    "Swirl": 0.6,
    "Superconduct": 1.5,
    "Electro-Charged": 2.0,
    "Overloaded": 2.75,
    "Shattered": 3.0,
    "Bloom": 2.0,
    "Hyperbloom": 3.0,
    "Burgeon": 3.0,
    "Burning": 0.25,
}

level_multipliers = {
    90: 1446.85,
    95: 1561.47,
    100: 1674.81
}

LUNAR_WEIGHTS = (1.0, 0.5, 1 / 12, 1 / 12)
STELLAR_SWIRL_WEIGHTS = (0.6, 0.3, 0.05, 0.05)

# --- Functions ---

def calculate_reaction_ls_damage(
        contributors: list[tuple[entities.Character, list[models.BuffRule]]],
        element: str,
        enemy: entities.Enemy,
        reaction: str,
        rxn_coeff: float,
) -> float:
    """
    Calculates multi-contributor Lunar or Stellar reaction damage.

    Args:
        contributors (list[tuple[entities.Character, list[models.BuffRule]]]): A list of contributing characters and their active buffs.
        element (str): The element of the attack.
        enemy (entities.Enemy): The Enemy being attacked.
        reaction (str): The reaction being triggered.
        rxn_coeff (float): The coefficient of the reaction.

    Returns:
        float: The multi-contributor Lunar or Stellar reaction damage.
    """
    individual_damages: list[float] = []

    for char, active_buffs in contributors:
        stats = char.out_of_combat_stats()
        for buff in active_buffs:
            if buff.element_filters and element not in buff.element_filters:
                continue
            if buff.ability_filters and not (reaction in buff.ability_filters or "Reaction" in buff.ability_filters):
                continue
            stats[buff.stat] = stats.get(buff.stat, 0) + buff.base_value

        em = stats.get("Elemental Mastery", 0.0)
        lvl_mult = level_multipliers.get(char.lvl, 0.0)
        effective_res = enemy.resistances.get(element, 0.1) - stats.get("RES Shred", 0.0)

        if effective_res < 0:
            res_mult = 1 - effective_res / 2
        elif 0.75 > effective_res >= 0:
            res_mult = 1 - effective_res
        else:
            res_mult = 1 / (4 * effective_res + 1)

        rxn_base_dmg_p = 1 + stats.get("Reaction Base DMG%", 0.0)
        rxn_dmg_p = (
                1
                + ((6 * em) / (em + 2000))
                + stats.get("Reaction DMG%", 0.0)
                + stats.get(f"{reaction} DMG%", 0.0)
                + stats.get("Stellar DMG%" if "Stellar" in reaction else "Lunar DMG%", 0.0)
        )
        flat_dmg = stats.get("Reaction Flat DMG", 0.0)
        elevation_mult = 1 + stats.get("Elevation", 0.0)
        crit_mult = 1 + max(0, min(1, stats.get("Crit Rate", 0.0))) * stats.get("Crit Damage", 0.0)
        rxn_coeff_up = (rxn_coeff + stats.get("Base Reaction Coefficient", 0.0)) * (1 + stats.get("Reaction Base Mult", 0.0))
        damage = ((lvl_mult * rxn_coeff_up * rxn_base_dmg_p * rxn_dmg_p) + flat_dmg) * elevation_mult * crit_mult * res_mult
        individual_damages.append(damage)

    individual_damages.sort(reverse=True)
    weights = STELLAR_SWIRL_WEIGHTS if "Stellar" in reaction else LUNAR_WEIGHTS
    return sum(w * d for w, d in zip(weights, individual_damages))

def calculate_hit_damage(attacker: entities.Character, ability: models.Ability, enemy: entities.Enemy, active_buffs: list[models.BuffRule], reaction: str | None = None):
    """
    Calculates the damage the inputted attack would deal.

    Args:
        attacker (entities.Character): The attacking character.
        ability (models.Ability): The ability used by the attacker.
        enemy (entities.Enemy): The enemy being attacked by the attacker.
        active_buffs (list[models.BuffRule]): The buffs currently active on the attacker.
        reaction (str | None): The reaction triggered by the ability.

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
        if buff.stat == "Original DMG Mult":
            base_stats["Original DMG Mult"] = base_stats.get("Original DMG Mult", 1.0) * buff.base_value
        else:
            base_stats[buff.stat] = base_stats.get(buff.stat, 0.0) + buff.base_value

    base_stats["HP"] = base_stats["Base HP"] * (1 + base_stats["HP%"]) + base_stats["Flat HP"]
    base_stats["ATK"] = base_stats["Base ATK"] * (1 + base_stats["ATK%"]) + base_stats["Flat ATK"]
    base_stats["DEF"] = base_stats["Base DEF"] * (1 + base_stats["DEF%"]) + base_stats["Flat DEF"]

    em = base_stats.get("Elemental Mastery", 0.0)
    effective_res = enemy.resistances.get(ability.element, 0.1) - base_stats.get("RES Shred", 0.0)

    if effective_res < 0:
        res_mult = 1 - effective_res / 2
    elif 0.75 > effective_res >= 0:
        res_mult = 1 - effective_res
    else:
        res_mult = 1 / (4 * effective_res + 1)

    lvl_mult = level_multipliers.get(attacker.lvl, 0.0)
    rxn_dmg_bonus = base_stats.get("Reaction DMG%", 0.0) + base_stats.get(f"{reaction} DMG%", 0.0)
    # Transformative Reaction Branch
    if reaction in transformative_coefficients:
        rxn_coeff = transformative_coefficients[reaction]
        em_bonus = (16 * em) / (em + 2000)
        rxn_crit_mult = (
                1
                + max(0.0, min(1.0, base_stats.get("Reaction Crit Rate", 0.0) + base_stats.get(f"{reaction} Crit Rate", 0.0)))
                * (base_stats.get("Reaction Crit Damage", 0.0) + base_stats.get(f"{reaction} Crit Damage", 0.0))
        )

        return lvl_mult * rxn_coeff * (1 + em_bonus + rxn_dmg_bonus) * rxn_crit_mult * res_mult

    base_dmg = base_stats[ability.scaling_stat] * ability.mv
    base_dmg_mult = 1 * base_stats.get("Original DMG Mult", 1.0)
    crit_mult = 1 + max(0, min(1, base_stats["Crit Rate"])) * base_stats["Crit Damage"]

    # Standard Damage Branch
    if not (any(re.search(r"stellar|lunar", tag, re.IGNORECASE) for tag in ability.tags)):
        additive_base_dmg = base_stats.get("Flat DMG", 0.0)
        reaction_mult = 1.0

        if reaction in additive_coefficients:
            rxn_coeff = additive_coefficients[reaction]
            em_bonus = (5 * em) / (em + 1200)
            additive_base_dmg += lvl_mult * rxn_coeff * (1 + em_bonus + rxn_dmg_bonus)

        elif reaction in amplifying_coefficients:
            amp_base = amplifying_coefficients[reaction]
            em_bonus = (2.78 * em) / (em + 1400)
            reaction_mult = amp_base * (1 + em_bonus + rxn_dmg_bonus)

        dmg_p_mult = (
                1
                + base_stats.get("All DMG%", 0.0)
                + base_stats.get(f"{ability.element} DMG%", 0.0)
                + base_stats.get(f"{ability.attack_type} DMG%", 0.0)
        )
        def_mult = (attacker.lvl + 100) / (
                attacker.lvl + 100
                + ((enemy.lvl + 100) * (1 - base_stats.get("DEF Shred", 0.0)) * (1 - base_stats.get("DEF Ignore", 0.0)))
        )

        return ((base_dmg * base_dmg_mult) + additive_base_dmg) * dmg_p_mult * crit_mult * def_mult * res_mult * reaction_mult



    else:
        base_rxn_coefficient = (base_reaction_coefficients.get(ability.attack_type, 1.0) + base_stats.get("Base Reaction Coefficient", 0.0)) * (1 + base_stats.get("Reaction Base Mult", 0.0))
        rxn_base_dmg_p = 1 + base_stats.get("Reaction Base DMG%", 0.0)
        is_stellar = any(re.search(r"stellar", t, re.IGNORECASE) for t in [ability.attack_type, *ability.tags])
        rxn_dmg_p = (
                1
                + ((6 * em) / (em + 2000))
                + base_stats.get("Reaction DMG%", 0.0)
                + base_stats.get("Stellar DMG%" if is_stellar else "Lunar DMG%", 0.0)
        )
        additive_base_dmg = base_stats.get("Reaction Flat DMG", 0.0)
        elevation_mult = 1 + base_stats.get("Elevation", 0.0)

        return ((base_rxn_coefficient * base_dmg * base_dmg_mult * rxn_base_dmg_p * rxn_dmg_p) + additive_base_dmg) * elevation_mult * crit_mult * res_mult





