from dataclasses import dataclass
import engine.entities as entities
from engine.models import Ability
import copy
import heapq
from engine.damage import calculate_hit_damage, transformative_coefficients, calculate_reaction_ls_damage

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
    ("Dendro", "Pyro"): ("Burning", 0.0),
    ("Pyro", "Dendro"): ("Burning", 0.0),
    ("Quicken", "Hydro"): ("Bloom", 0.5),
    ("Quicken", "Pyro"): ("Burning", 0.0),
}

transformative_elements = {
    "Overloaded": "Pyro",
    "Electro-Charged": "Electro",
    "Superconduct": "Cryo",
    "Bloom": "Dendro",
    "Hyperbloom": "Dendro",
    "Burgeon": "Dendro",
    "Shattered": "Physical",
    "Burning": "Pyro"
}

# --- Classes ---

@dataclass
class RotationStep:
    character: entities.Character
    ability: entities.Ability
    swap_delay: float = 0.0

@dataclass
class DendroCore:
    creator: entities.Character
    active: bool = True

@dataclass
class StellarVortex:
    triggers: int
    contributors: dict[str, entities.Character]
    is_lv2: bool = False
    active: bool = True

@dataclass
class SimEvent:
    """
    Blueprint for a simulation event.

    Attributes:
        timestamp (float): The time which the event occurs.
        event_type (str): The type of event occurs: "CAST", "HIT", "REACTION_TICK", or "CORE_EXPIRE".
        character (entities.Character): The character the event corresponds to.
        ability (entities.Ability): The ability occurring during the event.
        core (DendroCore): A core created from Bloom.
    """
    timestamp: float
    event_type: str
    character: entities.Character
    ability: entities.Ability
    core: DendroCore | None = None
    vortex: StellarVortex | None = None

    def __lt__(self, other) -> bool:
        return (self.timestamp, self.event_type) < (other.timestamp, other.event_type)


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

def update_auras(enemy : entities.Enemy, timestamp: float):
    """
    Updates an enemies' Auras for how much time has passed.

    Args:
        enemy (entities.Enemy): The enemy to update auras for.
        timestamp (float): The time at which this function was called.
    """
    dt = timestamp - enemy.last_aura_time
    enemy.last_aura_time = timestamp
    burning_drain = 0.4 if "Burning" in enemy.auras else 0.0

    for elm in list(enemy.auras.keys()):
        gu, rate = enemy.auras[elm]
        total_rate = rate + (burning_drain if elm in ("Dendro", "Quicken") else 0.0)
        new_gu = gu - dt * total_rate
        if new_gu > 0:
            enemy.auras[elm][0] = new_gu
        else:
            enemy.auras.pop(elm)

    if "Burning" in enemy.auras and not ("Dendro" in enemy.auras or "Quicken" in enemy.auras):
        enemy.auras.pop("Burning")

def apply_aura(enemy: entities.Enemy, element: str, gauge_units: float):
    """
    Applies an elemental aura to an enemy.

    Args:
        enemy (entities.Enemy): The enemy being applied the aura.
        element (str): The element of the aura being applied.
        gauge_units (float): The GU of the aura being applied.
    """
    if element not in ("Anemo", "Geo"):
        applied_gu = .8 * gauge_units
        decay_rate = applied_gu / (9.5 + 2.5 * gauge_units)
        if element in enemy.auras:
            existing_gu = enemy.auras[element][0]
            new_gu = max(existing_gu, applied_gu)
            if element == "Pyro":
                enemy.auras[element] = [new_gu, new_gu / (9.5 + 2.5 * new_gu)]
            else:
                enemy.auras[element][0] = new_gu
        else:
            enemy.auras[element] = [applied_gu, decay_rate]

def decrement_aura(enemy: entities.Enemy, aura: str, gauge_units: float):
    """
    Decrements an elemental aura, and removes it if negative.

    Args:
        enemy (entities.Enemy): The enemy whose auras are decremented.
        aura (str): The aura to decrement.
        gauge_units (float): The GU being removed from the aura.
    """
    enemy.auras[aura][0] -= gauge_units
    if enemy.auras[aura][0] <= 0:
        enemy.auras.pop(aura)

def make_rxn_ability(name: str, element: str) -> Ability:
    """
    Creates a lightweight ability for a reaction.

    Args:
        name (str): The name of the reaction.
        element (str): The element of the reaction.

    Returns:
        Ability: A lightweight ability corresponding to the reaction.
    """
    return Ability(name, name, 0.0, element=element, attack_type="Reaction")

def process_ec_tick(enemy: entities.Enemy, events: list[SimEvent], timestamp: float, ec_owner: entities.Character) -> float | None:
    """
    Drains 0.4 GU from Electro & Hydro, and schedules the next EC tick if both auras still exist.

    Args:
        enemy (entities.Enemy): The enemy with the auras.
        events (list[SimEvent]): A list of SimEvent objects.
        timestamp (float): The time at which this function was called.
        ec_owner (entities.Character): The owner of the EC tick.

    Returns:
        float | None: The time of the next EC tick if the auras still exist, else None.
    """
    for elm in ("Electro", "Hydro"):
        decrement_aura(enemy, elm, 0.4)

    if "Hydro" in enemy.auras and "Electro" in enemy.auras:
        next_tick = timestamp + 1.0
        rxn_ability = make_rxn_ability("Electro-Charged", "Electro")
        heapq.heappush(events, SimEvent(next_tick, "REACTION_TICK", ec_owner, rxn_ability))
        return next_tick
    return None

def process_burning_tick(enemy: entities.Enemy, events: list[SimEvent], timestamp: float, burning_owner: entities.Character) -> float | None:
    """
    Drains 0.4 GU from Electro & Hydro, and schedules the next EC tick if both auras still exist.

    Args:
        enemy (entities.Enemy): The enemy with the auras.
        events (list[SimEvent]): A list of SimEvent objects.
        timestamp (float): The time at which this function was called.
        burning_owner (entities.Character): The owner of the Burning tick.

    Returns:
        float | None: The time of the next Burning tick if the auras still exist, else None.
    """
    if "Burning" in enemy.auras:
        next_tick = timestamp + 0.25
        rxn_ability = make_rxn_ability("Burning", "Pyro")
        heapq.heappush(events, SimEvent(next_tick, "REACTION_TICK", burning_owner, rxn_ability))
        return next_tick
    return None

def process_lc_tick(
        enemy: entities.Enemy,
        events: list[SimEvent],
        timestamp: float,
        thundercloud_expire: float,
        lc_owner: entities.Character,
) -> float | None:
    for elm in ("Electro", "Hydro"):
        decrement_aura(enemy, elm, 0.4)

    next_tick = timestamp + 2.0
    if "Hydro" in enemy.auras and "Electro" in enemy.auras and next_tick <= thundercloud_expire:
        rxn_ability = make_rxn_ability("Lunar-Charged", "Electro")
        heapq.heappush(events, SimEvent(next_tick, "REACTION_TICK", lc_owner, rxn_ability))
        return next_tick
    return None

def resolve_reaction_override(team: list[entities.Character], reaction: str, search_elm: str) -> str:
    """
    Overrides a reaction if a team member overrides it.

    Args:
        team (list[entities.Character]): A team of characters.
        reaction (str): The reaction to override.
        search_elm (str): An element to check Swirl against.

    Returns:
        str: The overridden reaction, or the original reaction if not overridden.
    """
    if reaction == "Swirl" and search_elm != "Cryo":
        return reaction
    if reaction == "Crystallize" and search_elm != "Hydro":
        return reaction
    for char in team:
        if reaction in char.reaction_override:
            return char.reaction_override[reaction]
    return reaction

def detonate_vortex(
        vortex: StellarVortex,
        enemy: entities.Enemy,
        buffs_by_char: dict[str, list[entities.BuffRule]],
        damage_by_char: dict[str, float],
) -> None:
    coeff = 3 if vortex.is_lv2 or vortex.triggers >= 3 else 2.0
    contributors = [(char, buffs_by_char[char.name]) for char in vortex.contributors.values()]
    damage = calculate_reaction_ls_damage(contributors, "Cryo", enemy, "Stellar Swirl", coeff)
    trigger_char = next(iter(vortex.contributors.values()))
    damage_by_char[trigger_char.name] += damage

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

    heapq.heapify(events)

    all_state_rules: list[entities.StateRule] = []
    all_buff_rules: list[entities.BuffRule] = []
    # COME BACK TO THIS, Reaccess if this is the best way to handle Anastasya's A4
    polestar_bonus_stacks = 0
    polestar_instant_buff = False
    instant_lv2_vortex = False
    has_lunar_domain_a4 = False

    for character in team:
        all_state_rules.extend(character.state_rules)
        all_buff_rules.extend(character.buff_rules)
        all_state_rules.extend(character.weapon.state_rules)
        all_buff_rules.extend(character.weapon.buff_rules)
        if len(character.artifact_set) == 1:
            all_state_rules.extend(character.artifact_set[0].state_rules)
            all_buff_rules.extend(character.artifact_set[0].buff_rules)
        polestar_bonus_stacks += character.polestar_bonus_stacks
        polestar_instant_buff = polestar_instant_buff or character.polestar_instant_buff
        instant_lv2_vortex = instant_lv2_vortex or character.instant_lv2_vortex
        has_lunar_domain_a4 = has_lunar_domain_a4 or character.lunar_domain_a4

    active_states: dict[str, list[float]] = {}
    icd_tracker: dict[ tuple[str, str] , list[float]] = {}
    aura_owners: dict[str, entities.Character] = {}

    on_field_character = None
    damage_by_char = {char.name: 0.0 for char in team}

    ec_owner: entities.Character | None = None
    next_ec_time: float | None = None

    burning_owner: entities.Character | None = None
    next_burning_time: float | None = None

    dendro_cores: list[DendroCore] = []

    polestar_expire: float = 0.0
    polestar_buff_active: bool = False
    polestar_record_end: float = 0.0
    polestar_recorded_hits: int = 0
    polestar_active_stacks: int = 0

    active_vortex: StellarVortex | None = None
    detonate_early_vortex: StellarVortex | None = None
    stellar_swirl_contributors: dict[str, entities.Character] = {}
    last_vortex_upgrade_time: float = -1.0

    thundercloud_expire: float = 0.0
    lc_owner: entities.Character | None = None
    next_lc_time: float | None = None
    lc_contributors: dict[str, entities.Character] = {}

    vd_window_end: float = 0.0
    next_vd_time: float | None = None
    moonridge_window_end: float = 0.0
    moonridge_gained_count: int = 0

    lunar_crystallize_count: int = 0
    lcrys_contributors: dict[str, entities.Character] = {}
    trigger_moondrift_harmony: bool = False


    while events:
        event = heapq.heappop(events)

        if event.timestamp > thundercloud_expire:
            lc_contributors.clear()
            next_lc_time = None

        if event.timestamp >= polestar_expire:
            polestar_buff_active = False
            polestar_record_end = 0.0
            polestar_recorded_hits = 0
            polestar_active_stacks = 0

        while 0.0 < polestar_record_end <= event.timestamp:
            polestar_buff_active = True
            polestar_active_stacks = min(12, polestar_recorded_hits + polestar_bonus_stacks)
            polestar_recorded_hits = 0
            polestar_record_end += 4.0

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

        lunar_domain_enhanced = has_lunar_domain_a4 and len(active_states.get("Lunar Domain", [])) > 0

        triggered_reactions: list[tuple[str, str | None]] = []

        if event.event_type == "HIT":
            update_auras(enemy, event.timestamp)

            applies_element = check_icd(icd_tracker, event)

            if "Frozen" in enemy.auras and (event.ability.is_blunt or event.ability.element == "Geo"):
                enemy.auras.pop("Frozen")
                triggered_reactions.append(("Shattered", "Physical"))

            if dendro_cores and event.ability.element in ("Pyro", "Electro"):
                rxn_name = "Hyperbloom" if event.ability.element == "Electro" else "Burgeon"
                for _ in range(min(2,len(dendro_cores))):
                    core = dendro_cores.pop(0)
                    core.active = False
                    triggered_reactions.append((rxn_name, "Dendro"))

            if applies_element:
                if event.ability.element in ("Hydro", "Electro") and event.timestamp <= thundercloud_expire:
                    lc_contributors[event.character.name] = event.character

                if event.ability.element in ("Cryo", "Electro") and event.timestamp < polestar_expire:
                    polestar_recorded_hits += 1

                for aura_elm in sorted(enemy.auras.keys(), key=lambda el: (el != "Quicken", el != "Burning")):
                    search_elm = "Cryo" if aura_elm == "Frozen" else ("Pyro" if aura_elm == "Burning" else aura_elm)
                    if (search_elm, event.ability.element) in REACTIONS:
                        reaction, tax = REACTIONS[(search_elm, event.ability.element)]
                        reaction = resolve_reaction_override(team, reaction, search_elm)
                        rxn_element = transformative_elements.get(reaction, search_elm)
                        if reaction == "Quicken":
                            quicken_gu = max(enemy.auras.get(reaction, [0.0])[0],
                                             min(enemy.auras[aura_elm][0], event.ability.gauge_units))
                            enemy.auras["Quicken"] = [quicken_gu, quicken_gu / (quicken_gu * 5 + 6)]

                        if reaction == "Frozen":
                            frozen_gu = 2 * min(enemy.auras[aura_elm][0], event.ability.gauge_units)
                            duration = 2 * (5 * frozen_gu + 4) ** 0.5 - 4
                            enemy.auras["Frozen"] = [frozen_gu, frozen_gu / duration]

                        if reaction == "Electro-Charged":
                            apply_aura(enemy, event.ability.element, event.ability.gauge_units)
                            aura_owners[event.ability.element] = event.character
                            ec_owner = event.character
                            if next_ec_time is None:
                                triggered_reactions.append(("Electro-Charged", "Electro"))
                                next_ec_time = process_ec_tick(enemy, events, event.timestamp, ec_owner)
                            break

                        if reaction == "Burning":
                            apply_aura(enemy, event.ability.element, event.ability.gauge_units)
                            aura_owners[event.ability.element] = event.character
                            enemy.auras["Burning"] = [2.0, 0.0]
                            burning_owner = event.character
                            if next_burning_time is None:
                                next_burning_time = process_burning_tick(enemy, events, event.timestamp, burning_owner)
                            break

                        decrement_aura(enemy, aura_elm, event.ability.gauge_units * tax)

                        if reaction in ("Bloom", "Lunar-Bloom"):
                            if reaction == "Lunar-Bloom":
                                vd_window_end = event.timestamp + 2.5
                                if next_vd_time is None:
                                    next_vd_time = event.timestamp + 2.5
                                    heapq.heappush(events, SimEvent(next_vd_time, "VERDANT_DEW", event.character, make_rxn_ability("Lunar-Bloom", "Dendro")))

                                if lunar_domain_enhanced:
                                    if event.timestamp >= moonridge_window_end:
                                        moonridge_window_end = event.timestamp + 18.0
                                        moonridge_gained_count = 0
                                    moonridge_timers = active_states.setdefault("Moonridge Dew", [])
                                    if moonridge_gained_count < 3 and len(moonridge_timers) < 3:
                                        moonridge_timers.append(float("inf"))
                                        moonridge_gained_count += 1
                            core = DendroCore(creator = event.character)
                            dendro_cores.append(core)
                            bloom_ability = make_rxn_ability("Bloom", "Dendro")
                            heapq.heappush(events, SimEvent(event.timestamp + 6.0, "CORE_EXPIRE", event.character, bloom_ability, core=core))

                            if len(dendro_cores) > 5:
                                overflow = dendro_cores.pop(0)
                                overflow.active = False
                                heapq.heappush(events, SimEvent(event.timestamp, "CORE_EXPIRE", overflow.creator, bloom_ability))
                            break

                        if reaction == "Stellar-Conduct":
                            active_states["Radiance: Stellar-Conduct"] = [event.timestamp + 8.0]
                            if event.timestamp >= polestar_expire:
                                polestar_record_end = event.timestamp + 4.0
                                polestar_recorded_hits = 0
                                if polestar_instant_buff:
                                    polestar_buff_active = True
                                    polestar_active_stacks = min(12, polestar_bonus_stacks)
                                else:
                                    polestar_buff_active = False
                                    polestar_active_stacks = 0

                            polestar_expire = event.timestamp + 6.0
                            break

                        if reaction == "Stellar Swirl":
                            active_states["Radiance: Stellar Swirl"] = [event.timestamp + 8.0]
                            hit_contributors = {event.character.name: event.character}
                            if "Cryo" in aura_owners:
                                hit_contributors[aura_owners["Cryo"].name] = aura_owners["Cryo"]

                            triggered_reactions.append(("Stellar Swirl", "Anemo"))
                            stellar_swirl_contributors = hit_contributors

                            if active_vortex is None:
                                is_lv2 = False
                                if instant_lv2_vortex and (event.timestamp - last_vortex_upgrade_time) >= 1.0:
                                    is_lv2 = True
                                    last_vortex_upgrade_time = event.timestamp
                                active_vortex = StellarVortex(triggers=1, contributors=dict(hit_contributors), is_lv2=is_lv2)
                                vortex_ability = make_rxn_ability("Stellar Swirl", "Cryo")
                                heapq.heappush(events, SimEvent(event.timestamp + 3.0, "VORTEX_EXPLODE", event.character, vortex_ability, vortex= active_vortex))
                            else:
                                active_vortex.triggers += 1
                                active_vortex.contributors.update(hit_contributors)
                                if active_vortex.triggers >= 6:
                                    active_vortex.active = False
                                    detonate_early_vortex = active_vortex
                                    active_vortex = None
                            break

                        if reaction == "Lunar-Charged":
                            apply_aura(enemy, event.ability.element, event.ability.gauge_units)
                            aura_owners[event.ability.element] = event.character
                            if event.timestamp > thundercloud_expire:
                                lc_contributors.clear()
                            for elm in ("Hydro", "Electro"):
                                if elm in aura_owners:
                                    lc_contributors[aura_owners[elm].name] = aura_owners[elm]
                            lc_contributors[event.character.name] = event.character
                            lc_owner = event.character
                            thundercloud_expire = event.timestamp + 6.0
                            if next_lc_time is None and (event.timestamp + 2.0) <= thundercloud_expire:
                                next_lc_time = event.timestamp + 2.0
                                heapq.heappush(events, SimEvent(next_lc_time, "REACTION_TICK", lc_owner, make_rxn_ability("Lunar-Charged", "Electro")))
                            break

                        if reaction == "Lunar-Crystallize":
                            active_states["Moondrift"] = [event.timestamp + 15.0]
                            if "Hydro" in aura_owners:
                                lcrys_contributors[aura_owners["Hydro"].name] = aura_owners["Hydro"]
                            lcrys_contributors[event.character.name] = event.character
                            lunar_crystallize_count += 1
                            if lunar_crystallize_count % 3 == 0:
                                trigger_moondrift_harmony = True
                            break

                        triggered_reactions.append((reaction, rxn_element))
                        break
                else:
                    apply_aura(enemy, event.ability.element, event.ability.gauge_units)
                    aura_owners[event.ability.element] = event.character

        elif event.event_type == "REACTION_TICK":
            rxn_name = event.ability.parent_name
            if rxn_name == "Electro-Charged":
                if event.timestamp != next_ec_time:
                    continue
                update_auras(enemy, event.timestamp)
                if not ("Hydro" in enemy.auras and "Electro" in enemy.auras):
                    next_ec_time = None
                    continue
            elif rxn_name == "Burning":
                if event.timestamp != next_burning_time:
                    continue
                update_auras(enemy, event.timestamp)
                if "Burning" not in enemy.auras:
                    next_burning_time = None
                    continue
            elif rxn_name == "Lunar-Charged":
                if event.timestamp != next_lc_time or event.timestamp > thundercloud_expire:
                    continue
                update_auras(enemy, event.timestamp)
                if not ("Hydro" in enemy.auras and "Electro" in enemy.auras):
                    next_lc_time = None
                    continue

        elif event.event_type == "CORE_EXPIRE":
            if event.core is not None and not event.core.active:
                continue

        elif event.event_type == "VORTEX_EXPLODE":
            if event.vortex is not None and not event.vortex.active:
                continue

        elif event.event_type == "VERDANT_DEW":
            if event.timestamp == next_vd_time:
                dew_timers = active_states.setdefault("Verdant Dew", [])
                if len(dew_timers) < 3:
                    dew_timers.append(float("inf"))
                if event.timestamp < vd_window_end:
                    next_vd_time = event.timestamp + 2.5
                    heapq.heappush(events, SimEvent(next_vd_time, "VERDANT_DEW", event.character, event.ability))
                else:
                    next_vd_time = None
            continue

        if event.event_type in ("HIT", "REACTION_TICK", "CORE_EXPIRE", "VORTEX_EXPLODE"):
            team_stats = {char.name: char.out_of_combat_stats() for char in team}

            buffs_by_char: dict[str, list[entities.BuffRule]] = {char.name: [] for char in team}

            for order in (0, 1, 2, 3):
                for buff in all_buff_rules:
                    if buff.scaling_order == order and (
                            all(len(active_states.get(state, [])) >= buff.min_stacks for state in
                                buff.required_states)):
                        copied_buff = copy.copy(buff)
                        if order != 0:
                            scaling_val = team_stats[buff.character_source].get(buff.scaling_stat, 0.0)
                            buff_val = scaling_val * buff.base_value
                            if buff.scale_with_stacks and buff.required_states:
                                buff_val *= len(active_states.get(buff.required_states[0], []))
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
                                    team_stats[char.name][buff.stat] = (team_stats[char.name].get(copied_buff.stat,0.0)
                                                                        + copied_buff.base_value)
                                buffs_by_char[char.name].append(copied_buff)
                for c, stats in team_stats.items(): recalc_total(stats)

            if event.timestamp < polestar_expire:
                polestar_buffs = [
                    entities.BuffRule(
                        buff_id="POLESTAR_PHYS_RES",
                        buff_name="Polestar Physical Res Shred",
                        character_source="Polestar Field",
                        stat="RES Shred",
                        base_value=0.40,
                        target_scope="TEAM",
                        element_filters=["Physical"],
                    ),
                ]
                if polestar_buff_active:
                    polestar_dmg_bonus = 0.28 + 0.01 * polestar_active_stacks
                    polestar_buffs.extend([
                        entities.BuffRule(
                            buff_id= "POLESTAR_CRYO_DMG",
                            buff_name= "Polestar Cryo DMG%",
                            character_source="Polestar Field",
                            stat="Cryo DMG%",
                            base_value=polestar_dmg_bonus,
                            target_scope="TEAM",
                        ),
                        entities.BuffRule(
                            buff_id="POLESTAR_ELECTRO_DMG",
                            buff_name="Polestar Electro DMG%",
                            character_source="Polestar Field",
                            stat="Electro DMG%",
                            base_value=polestar_dmg_bonus,
                            target_scope="TEAM",
                        ),
                    ])
                    if polestar_active_stacks >= 1:
                        polestar_buffs.append(
                            entities.BuffRule(
                                buff_id="POLESTAR_BASE_REACTION",
                                buff_name="Polestar Base Reaction Coefficient",
                                character_source="Polestar Field",
                                stat="Base Reaction Coefficient",
                                base_value=0.40 + 0.05 * polestar_active_stacks,
                                target_scope="TEAM",
                                ability_filters=["Stellar-Conduct"],
                            )
                        )
                for char in team:
                    buffs_by_char[char.name].extend(polestar_buffs)

            if event.event_type == "HIT":
                # Override for Stellar or Lunar Reactions
                # for char in team:
                #    reaction = char.reaction_override[reaction] if reaction in char.reaction_override.keys() else reaction

                # Modifies the talent hit with at most 1 amp/add reaction
                talent_rxn = next((rxn for rxn, _ in triggered_reactions if rxn not in transformative_coefficients and rxn != "Stellar Swirl"), None)
                event_damage = calculate_hit_damage(event.character, event.ability, enemy, buffs_by_char[event.character.name], talent_rxn)

                # Adds a hit for every transformative reaction that occurs
                for rxn, rxn_elm in triggered_reactions:
                    if rxn in transformative_coefficients:
                        rxn_ability = Ability(
                            parent_name= rxn,
                            component_name= rxn,
                            mv= 0.0,
                            element= rxn_elm,
                            attack_type= "Reaction"
                        )
                        event_damage += calculate_hit_damage(event.character, rxn_ability, enemy, buffs_by_char[event.character.name], rxn)
                    elif rxn == "Stellar Swirl":
                        contributors = [(char, buffs_by_char[char.name]) for char in stellar_swirl_contributors.values()]
                        event_damage += calculate_reaction_ls_damage(contributors, "Anemo", enemy, "Stellar Swirl", 0.75)

                damage_by_char[event.character.name] += event_damage
                if detonate_early_vortex is not None:
                    detonate_vortex(detonate_early_vortex, enemy, buffs_by_char, damage_by_char)
                    detonate_early_vortex = None
                    if event.timestamp < polestar_expire:
                        polestar_recorded_hits += 1
                if trigger_moondrift_harmony:
                    contributors = [(char, buffs_by_char[char.name]) for char in lcrys_contributors.values()]
                    strike_mult = 1.33 if lunar_domain_enhanced else 1.0
                    harmony_dmg = 3 * strike_mult * calculate_reaction_ls_damage(contributors, "Geo", enemy, "Lunar-Crystallize", 0.96)
                    damage_by_char[event.character.name] += harmony_dmg
                    lcrys_contributors.clear()
                    trigger_moondrift_harmony = False

            elif event.event_type in ("REACTION_TICK", "CORE_EXPIRE"):
                rxn_name = event.ability.parent_name
                if rxn_name == "Lunar-Charged":
                    contributors = [(char, buffs_by_char[char.name]) for char in lc_contributors.values()]
                    strike_mult = 1.33 if lunar_domain_enhanced else 1.0
                    damage_by_char[lc_owner.name] += strike_mult * calculate_reaction_ls_damage(
                        contributors, "Electro", enemy,"Lunar-Charged", 1.8
                    )
                    next_lc_time = process_lc_tick(enemy, events, event.timestamp, thundercloud_expire, lc_owner)
                else:
                    owner = (
                        ec_owner if rxn_name == "Electro-Charged"
                        else burning_owner if rxn_name == "Burning"
                        else event.character # Covers for Bloom
                    )
                    damage_by_char[owner.name] += calculate_hit_damage(owner, event.ability, enemy, buffs_by_char[owner.name], rxn_name)
                    if rxn_name == "Electro-Charged":
                        next_ec_time = process_ec_tick(enemy, events, event.timestamp, ec_owner)
                    elif rxn_name == "Burning":
                        next_burning_time = process_burning_tick(enemy, events, event.timestamp, burning_owner)

            elif event.event_type == "VORTEX_EXPLODE":
                detonate_vortex(event.vortex, enemy, buffs_by_char, damage_by_char)
                if event.timestamp < polestar_expire:
                    polestar_recorded_hits += 1

    return damage_by_char