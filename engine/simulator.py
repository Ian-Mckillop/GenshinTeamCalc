from dataclasses import dataclass
import engine.entities as entities
from engine.models import Ability
import copy

from engine.damage import calculate_hit_damage, transformative_coefficients

# --- Constants ---

REACTIONS = {
    ("Cryo", "Pyro"): ("Melt", 2.0),
    ("Pyro", "Cryo"): ("Reverse Melt", 0.5),
    ("Pyro", "Hydro"): ("Vaporize", 2.0),
    ("Hydro", "Pyro"): ("Reverse Vaporize", 0.5),
    ("Cryo", "Electro"): ("Superconduct", 1.0),
    ("Electro", "Cryo"): ("Superconduct", 1.0),
    ("Cryo", "Anemo"): ("Swirl", 0.5),
    ("Pyro", "Anemo"): ("Swirl", 0.5),
    ("Hydro", "Anemo"): ("Swirl", 0.5),
    ("Electro", "Anemo"): ("Swirl", 0.5),
    ("Electro", "Hydro"): ("Electro-Charged", 0.0),
    ("Hydro", "Electro"): ("Electro-Charged", 0.0),
    ("Dendro", "Hydro"): ("Bloom", 2.0),
    ("Hydro", "Dendro"): ("Bloom", 0.5),
    ("Cryo", "Geo"): ("Crystallize", 0.5),
    ("Pyro", "Geo"): ("Crystallize", 0.5),
    ("Hydro", "Geo"): ("Crystallize", 0.5),
    ("Electro", "Geo"): ("Crystallize", 0.5),
    ("Electro", "Pyro"): ("Overloaded", 1.0),
    ("Pyro", "Electro"): ("Overloaded", 1.0),
    ("Hydro", "Cryo"): ("Frozen", 1.0),
    ("Cryo", "Hydro"): ("Frozen", 1.0),
    ("Electro", "Dendro"): ("Quicken", 1.0),
    ("Dendro", "Electro"): ("Quicken", 1.0),
    ("Quicken", "Electro"): ("Aggravate", 0.0),
    ("Quicken", "Dendro"): ("Spread", 0.0),
}

transformative_elements = {
    "Overloaded": "Pyro",
    "Electro-Charged": "Electro",
    "Superconduct": "Cryo",
    "Bloom": "Dendro",
    "Hyperbloom": "Dendro",
    "Burgeon": "Dendro",
    "Shattered": "Physical",
}

# --- Classes ---

@dataclass
class RotationStep:
    character: entities.Character
    ability: entities.Ability
    swap_delay: float = 0.0


@dataclass
class SimEvent:
    timestamp: float
    event_type: str
    character: entities.Character
    ability: entities.Ability

# --- Functions ---

def recalc_total(stats_dict):
    """
    Recalculates HP, ATK, and DEF for an inputted stat dictionary.

    Args:
        stats_dict (dict[str, float): A dictionary mapping stats to values.
    """
    stats_dict["HP"] = stats_dict["Base HP"] * (1 + stats_dict["HP%"]) + stats_dict["Flat HP"]
    stats_dict["ATK"] = stats_dict["Base ATK"] * (1 + stats_dict["ATK%"]) + stats_dict["Flat ATK"]
    stats_dict["DEF"] = stats_dict["Base DEF"] * (1 + stats_dict["DEF%"]) + stats_dict["Flat DEF"]

def check_icd(icd_tracker: dict, event: SimEvent) -> bool:
    """
    Checks whether an ability currently has internal cooldown.

    Args:
        icd_tracker (dict[ tuple[str, str] , list[float]]): A dictionary pairing (name, icd_group) tuple keys and 2 item [window start time, hit count] lists.
        event (SimEvent): A SimEvent corresponding to the ability being checked.

    Returns:
        bool: Whether an ability currently has internal cooldown.
    """
    if event.ability.gauge_units <= 0 or event.ability.element == "Physical":
        return False
    if event.ability.icd_group == "NONE":
        return True

    key = (event.character.name, event.ability.icd_group)
    if key not in icd_tracker or (event.timestamp - icd_tracker.get(key, [])[0]) >= event.ability.icd_time:
        icd_tracker[key] = [event.timestamp, 1]
        return True

    icd_tracker[key][1] += 1
    return ((icd_tracker[key][1] - 1) % event.ability.icd_hits) == 0


def simulate_rotation(team: list[entities.Character], enemy: entities.Enemy, rotation: list[RotationStep]):
    """
    Calculates the damage each character in a team deals, for a given rotation.

    Args:
        team (list[entities.Character]): The team of characters to simulate.
        enemy (entities.Enemy): the enemy to simulate damage against.
        rotation (list[RotationStep]): The set of attacks to simulate.

    Returns:
        The amount of damage each character in the team deals.
    """
    current_time = 0.0
    on_field_character = None
    events = []

    for step in rotation:
        if step.character != on_field_character and on_field_character is not None:
            current_time += step.swap_delay
        on_field_character = step.character

        summon_ids = {a.summon_id for a in [step.ability, *step.ability.sub_abilities] if a.summon_id is not None}
        events = [e for e in events if not (
                    e.character == step.character and e.event_type == "HIT" and e.ability.summon_id in summon_ids and e.timestamp > current_time)]

        events.append(SimEvent(current_time, "CAST", step.character, step.ability))
        for offset in step.ability.hit_offsets:
            events.append(SimEvent(current_time + offset, "HIT", step.character, step.ability))
        for sub in step.ability.sub_abilities:
            for offset in sub.hit_offsets:
                events.append(SimEvent(current_time + offset, "HIT", step.character, sub))
        current_time += step.ability.cast_duration

    events.sort(key=lambda e: (e.timestamp, e.event_type))

    all_state_rules: list[entities.StateRule] = []
    all_buff_rules: list[entities.BuffRule] = []
    for character in team:
        all_state_rules.extend(character.state_rules)
        all_buff_rules.extend(character.buff_rules)
        all_state_rules.extend(character.weapon.state_rules)
        all_buff_rules.extend(character.weapon.buff_rules)
        if len(character.artifact_set) == 1:
            all_state_rules.extend(character.artifact_set[0].state_rules)
            all_buff_rules.extend(character.artifact_set[0].buff_rules)

    active_states: dict[str, list[float]] = {}
    icd_tracker: dict[ tuple[str, str] , list[float]] = {}

    on_field_character = None
    damage_by_char = {char.name: 0.0 for char in team}

    for event in events:
        event_tags = [event.event_type, event.ability.attack_type, event.ability.element, *event.ability.tags]
        # clean out expired timestamps
        active_states = {state_name: [t for t in times if t > event.timestamp] for state_name, times in
                         active_states.items()}

        if event.event_type == "CAST":
            on_field_character = event.character

        for state in all_state_rules:

            if state.character_source == event.character.name and all(
                    tag in event_tags for tag in state.trigger_tags) and all(
                    len(active_states.get(req, [])) > 0 for req in state.required_states):
                expire_time = event.timestamp + state.base_duration
                timers = active_states.setdefault(state.state_id, [])

                if state.refresh_mode == "REFRESH ALL":
                    if len(timers) < state.max_stacks:
                        active_states[state.state_id].append(expire_time)
                    active_states[state.state_id] = [expire_time] * len(timers)

                elif state.refresh_mode == "INDEPENDENT":
                    active_states[state.state_id].append(expire_time)
                    if len(timers) > state.max_stacks:
                        active_states[state.state_id].pop(0)

        if event.event_type == "HIT":
            reaction = None
            rxn_element = None
            applies_element = check_icd(icd_tracker, event)
            dt = event.timestamp - enemy.last_aura_time
            enemy.last_aura_time = event.timestamp
            enemy.auras = {
                elm: [gu - dt * rate, rate]
                for elm, (gu, rate) in enemy.auras.items()
                if gu - dt * rate > 0
            }
            if applies_element:
                for aura_elm in sorted(enemy.auras.keys(), key=lambda el: el != "Quicken"):
                    if (aura_elm, event.ability.element) in REACTIONS:
                        reaction, tax = REACTIONS[(aura_elm, event.ability.element)]
                        rxn_element = transformative_elements.get(reaction, aura_elm)
                        if reaction == "Quicken":
                            quicken_gu = max(enemy.auras.get(reaction, [0.0])[0], min(enemy.auras[aura_elm][0], event.ability.gauge_units))
                            enemy.auras["Quicken"] = [quicken_gu, quicken_gu / (quicken_gu * 5 + 6) ]

                        enemy.auras[aura_elm][0] -= event.ability.gauge_units * tax
                        if enemy.auras[aura_elm][0] <= 0:
                            enemy.auras.pop(aura_elm)
                        break
                else:
                    if event.ability.element not in ("Anemo", "Geo"):
                        applied_gu = .8 * event.ability.gauge_units
                        decay_rate = applied_gu / (9.5 + 2.5 * event.ability.gauge_units)
                        if event.ability.element in enemy.auras:
                            existing_gu = enemy.auras[event.ability.element][0]
                            new_gu = max(existing_gu, applied_gu)
                            if event.ability.element == "Pyro":
                                enemy.auras[event.ability.element] = [new_gu, new_gu / (9.5 + 2.5 * new_gu)]
                            else:
                                enemy.auras[event.ability.element][0] = new_gu
                        else:
                            enemy.auras[event.ability.element] = [applied_gu, decay_rate]

            # Override for Stellar or Lunar Reactions
            for char in team:
                reaction = char.reaction_override[reaction] if reaction in char.reaction_override.keys() else reaction


            team_stats = {char.name: char.out_of_combat_stats() for char in team}
            
            current_buffs = []
            for order in (0,1,2,3):
                for buff in all_buff_rules:
                    if buff.scaling_order == order and (
                            all(len(active_states.get(state, [])) >= buff.min_stacks for state in buff.required_states)):
                        copied_buff = copy.copy(buff)
                        if order != 0:
                            scaling_val = team_stats[buff.character_source].get(buff.scaling_stat, 0.0)
                            buff_val = scaling_val * buff.base_value
                            if buff.scale_with_stacks and buff.required_states :
                                buff_val*= len(active_states.get(buff.required_states[0], []))
                            if buff.max_value > 0:
                                buff_val = min(buff_val, buff.max_value)
                            copied_buff.base_value = buff_val

                        if buff.scale_with_stacks and buff.required_states and order == 0:
                            copied_buff.base_value *= len(active_states.get(buff.required_states[0], []))
                        for char in team:
                            if buff.target_scope == "TEAM" or (
                                    buff.target_scope == "SELF" and buff.character_source == char.name) or (
                                    buff.target_scope == "ON_FIELD" and on_field_character.name == char.name):
                                if not buff.ability_filters and not buff.element_filters:
                                    team_stats[char.name][buff.stat] = team_stats[char.name].get(copied_buff.stat,0.0) + copied_buff.base_value
                                if char == event.character:
                                    current_buffs.append(copied_buff)
                for c, stats in team_stats.items(): recalc_total(stats)


            if reaction in transformative_coefficients:
                event_damage = calculate_hit_damage(event.character, event.ability, enemy, current_buffs)
                rxn_ability = Ability(
                    parent_name= reaction,
                    component_name= reaction,
                    mv= 0.0,
                    element= rxn_element,
                    attack_type= "Reaction"
                )

                event_damage += calculate_hit_damage(event.character, rxn_ability, enemy, current_buffs, reaction)
            else:
                event_damage = calculate_hit_damage(event.character, event.ability, enemy, current_buffs, reaction)
            damage_by_char[event.character.name] += event_damage

    return damage_by_char