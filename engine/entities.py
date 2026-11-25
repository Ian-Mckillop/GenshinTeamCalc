from dataclasses import field
from dataclasses import dataclass
from engine.models import StateRule, BuffRule, Ability
import copy

# --- Classes ---

@dataclass
class Weapon:
    """
    Blueprint for a weapon.
    """
    name: str
    type: str
    base_atk: float
    secondary_stats: dict[str, float] = field(default_factory=dict)
    state_rules: list[StateRule] = field(default_factory=list)
    buff_rules: list[BuffRule] = field(default_factory=list)

@dataclass
class ArtifactSet:
    """
    Blueprint for an artifact set.
    """
    name: str
    two_piece_stats: dict[str, float] = field(default_factory=dict)
    state_rules: list[StateRule] = field(default_factory=list)
    buff_rules: list[BuffRule] = field(default_factory=list)

@dataclass
class Character:
    """
    Blueprint for a playable character.
    Automatically adjusts base stats if character is lvl 100, and stamps character's name onto all attributed buffs.

    Attributes:
        reaction_override: A dictionary containing [Overridden Reaction, New Reaction].
    """
    name: str
    element: str
    constellation: int
    base_hp: float
    base_atk: float
    base_def: float
    weapon: Weapon
    weapon_type: str = ""
    lvl: int = 90
    artifact_set: list[ArtifactSet] = field(default_factory=list)
    ascension_stat: dict[str, float] = field(default_factory=dict)
    artifact_stats: dict[str, float] = field(default_factory=dict)
    abilities: list[Ability] = field(default_factory=list)
    state_rules: list[StateRule] = field(default_factory=list)
    buff_rules: list[BuffRule] = field(default_factory=list)
    reaction_override: dict[str, str] = field(default_factory=dict)
    # Convert these 4 into permanent states
    polestar_bonus_stacks: int = 0
    polestar_instant_buff: bool = False
    instant_lv2_vortex: bool = False
    lunar_domain_a4: bool = False


    def __post_init__(self):
        if not self.weapon_type:
            self.weapon_type = self.weapon.type

        # A lvl 100 Character has ~7.1% more Base HP and DEF, and ~22.5% more Base ATK then a lvl 90 Character.
        if self.lvl == 100:
            self.base_hp = self.base_hp * 1.071
            self.base_atk = self.base_atk * 1.225
            self.base_def = self.base_def * 1.071

        self.artifact_set = [copy.deepcopy(r) for r in self.artifact_set]
        self.weapon = copy.deepcopy(self.weapon)


        for state in self.state_rules:
            state.character_source = self.name

        if len(self.artifact_set) == 1:
            for state in self.artifact_set[0].state_rules:
                state.character_source = self.name

        for state in self.weapon.state_rules:
            state.character_source = self.name

        for buff in self.buff_rules:
            buff.character_source = self.name

        if len(self.artifact_set) == 1:
            for buff in self.artifact_set[0].buff_rules:
                buff.character_source = self.name

        for buff in self.weapon.buff_rules:
            buff.character_source = self.name


    def out_of_combat_stats(self):
        """
        Calculates what a character's stats are when no buffs are applied.

        Args:
            self: the object this is called from.

        Returns:
            A dictionary mapping stat names to total values across a character, their weapon, and their artifacts.
        """
        combat_stats = {
            "Base HP":  self.base_hp,
            "Base ATK": self.base_atk + self.weapon.base_atk,
            "Base DEF": self.base_def,
            "HP%": 0.0,
            "Flat HP": 0.0,
            "ATK%": 0.0,
            "Flat ATK": 0.0,
            "DEF%": 0.0,
            "Flat DEF": 0.0,
            "Elemental Mastery": 0.0,
            "Crit Rate": 0.05,
            "Crit Damage": 0.50,
            "Energy Recharge": 1.0,
        }

        list_of_stat_lists = [self.ascension_stat, self.artifact_stats, self.weapon.secondary_stats]
        for artifact_set in self.artifact_set:
            list_of_stat_lists.append(artifact_set.two_piece_stats)

        for stat_list in list_of_stat_lists:
            stats = stat_list.items()
            for stat_name, stat_value in stats:

                new_stat_value = combat_stats.get(stat_name, 0.0) + stat_value
                combat_stats[stat_name] = new_stat_value

        combat_stats["HP"] = combat_stats["Base HP"] * (1 + combat_stats["HP%"]) + combat_stats["Flat HP"]
        combat_stats["ATK"] = combat_stats["Base ATK"] * (1 + combat_stats["ATK%"]) + combat_stats["Flat ATK"]
        combat_stats["DEF"] = combat_stats["Base DEF"] * (1 + combat_stats["DEF%"]) + combat_stats["Flat DEF"]

        return combat_stats


@dataclass
class Enemy:
    """
    Blueprint for an Enemy.
    Defaults resistances to 10%.

    Attributes:
        lvl: Enemy Level.
        resistances: [Element, Resistance]
        auras: [Aura, [remaining_gu, decay_rate]]
        last_aura_time: The time since an aura was last applied.
    """
    lvl: int= 100
    resistances: dict[str, float] = field(default_factory=dict)
    auras: dict[str, list[float]] = field(default_factory=dict)
    last_aura_time: float = 0.0

    def __post_init__(self):
        # The default resistance in genshin is 10%.
        possible_resistances = ["Pyro", "Hydro", "Anemo", "Electro", "Dendro", "Cryo", "Geo", "Physical"]
        for resistance in possible_resistances:
            self.resistances.setdefault(resistance, 0.1)
