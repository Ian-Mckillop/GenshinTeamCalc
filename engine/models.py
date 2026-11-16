from dataclasses import field
from dataclasses import dataclass

@dataclass
class Ability:
    parent_name: str
    component_name : str
    mv: float
    hit_index: int = 1
    total_hits: int = 1
    scaling_stat: str=  "ATK"
    element: str = "Phys"
    attack_type: str = "Normal Attack"
    is_override: bool = False
    required_states: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)



@dataclass
class StateRule:
    state_id: str
    base_duration: float
    trigger_tags: list[str] = field(default_factory=list)
    required_states: list[str] = field(default_factory=list)
    freeze_state: list[str] = field(default_factory=list)
    termination_rules: list[str] = field(default_factory=list)
    termination_events: list[str] = field(default_factory=list)
    max_stacks: int = 1
    refresh_mode: str = "REFRESH_ALL"
    tick_interval: float = 0.0


@dataclass
class BuffRule:
    buff_id: str
    buff_name: str
    stat: str
    base_value: float
    character_source: str = "NONE"
    required_states: list[str] = field(default_factory=list)
    min_stacks: int = 1
    scale_with_stacks: bool = True
    buff_group: str = "NONE"
    scaling_stat: str= "NONE"
    max_value: float = 0.0
    duration_mode: str = "STATE_BOUND"
    linger_duration: float = 0.0
    target_scope: str = "TEAMWIDE"
    party_count_rule: str = "NONE"
    ability_filters: list[str] = field(default_factory=list)
    element_filters: list[str] = field(default_factory=list)