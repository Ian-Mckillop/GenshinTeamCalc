from dataclasses import field
from dataclasses import dataclass


# --- Constants ---

main_stat_dict = {
    "HP%": 0.466,
    "ATK%": 0.466,
    "DEF%": 0.583,
    "Elemental Mastery": 186.5,
    "Energy Recharge": 0.518,
    "Pyro DMG%": 0.466,
    "Hydro DMG%": 0.466,
    "Anemo DMG%": 0.466,
    "Electro DMG%": 0.466,
    "Dendro DMG%": 0.466,
    "Cryo DMG%": 0.466,
    "Geo DMG%": 0.466,
    "Physical DMG%": 0.583,
    "Crit Rate": 0.311,
    "Crit Damage": 0.622,
    "Healing Bonus": 0.359
}

# --- Classes ---

@dataclass
class Ability:
    """
    Blueprint for an ability.
    """
    parent_name: str
    component_name: str
    mv: float
    hit_index: int = 1
    total_hits: int = 1
    scaling_stat: str = "ATK"
    element: str = "Physical"
    attack_type: str = "Normal Attack"
    is_override: bool = False
    required_states: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    cast_duration: float = 0.0
    hit_offsets: list[float] = field(default_factory=list)
    summon_id: str | None = None
    sub_abilities: list["Ability"] = field(default_factory=list)
    gauge_units: float = 1.0
    icd_group: str = "DEFAULT"
    icd_time: float = 2.5
    icd_hits: int = 3


@dataclass
class StateRule:
    """
    Blueprint for a state.
    """
    state_id: str
    base_duration: float
    character_source: str = "NONE"
    trigger_tags: list[str] = field(default_factory=list)
    required_states: list[str] = field(default_factory=list)
    freeze_state: list[str] = field(default_factory=list)
    termination_rules: list[str] = field(default_factory=list)
    termination_events: list[str] = field(default_factory=list)
    max_stacks: int = 1
    refresh_mode: str = "REFRESH ALL"
    tick_interval: float = 0.0


@dataclass
class BuffRule:
    """
    Blueprint for a buff.
    """
    buff_id: str
    buff_name: str
    stat: str
    base_value: float
    character_source: str = "NONE"
    required_states: list[str] = field(default_factory=list)
    min_stacks: int = 1
    scale_with_stacks: bool = False
    buff_group: str = "NONE"
    scaling_stat: str = "NONE"
    max_value: float = 0.0
    scaling_order: int = 0
    duration_mode: str = "STATE_BOUND"
    linger_duration: float = 0.0
    target_scope: str = "TEAM"
    party_count_rule: str = "NONE"
    ability_filters: list[str] = field(default_factory=list)
    element_filters: list[str] = field(default_factory=list)

# --- Functions ---

def artifact_stats(sands, gob, circ, hp_p=0, flat_hp=0, atk_p=0, flat_atk=0, def_p=0, flat_def=0, em=0, cr=0, cd=0,
                   er=0):
    """
    Calculates combined 5* Artifact Mainstat & substat totals using KQM standards.

    Args:
        sands, gob, circ: stat keys matching main_stat_dict
        hp_p ... er: Distributed substat rolls.

    Returns:
        A dictionary mapping stat names to total values across all artifacts.
    """
    # KQM standards assume 2 substats per stat, plus 4780 Flat HP from the flower, and 311 Flat ATK from the feather.
    artifact_stat_dict = {
        "HP%": 0.05 * (2 + hp_p),
        "Flat HP": 254 * (2 + flat_hp) + 4780,
        "ATK%": 0.05 * (2 + atk_p),
        "Flat ATK": 17 * (2 + flat_atk) + 311,
        "DEF%": 0.062 * (2 + def_p),
        "Flat DEF": 20 * (2 + flat_def),
        "Elemental Mastery": 20 * (2 + em),
        "Crit Rate": 0.033 * (2 + cr),
        "Crit Damage": 0.066 * (2 + cd),
        "Energy Recharge": 0.0585 * (2 + er)
    }

    for artifact in [sands, gob, circ]:
        new_value = artifact_stat_dict.get(artifact, 0.0) + main_stat_dict[artifact]
        artifact_stat_dict[artifact] = new_value

    return artifact_stat_dict
