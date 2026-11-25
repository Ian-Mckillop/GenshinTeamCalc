from collections import Counter
import engine.entities as entities
import engine.models as models


def get_team_resonances(
    team: list[entities.Character],
) -> tuple[list[models.StateRule], list[models.BuffRule]]:
    """
    Returns (state_rules, buff_rules) for all active Elemental Resonances
    in a 4-character party.
    """
    if len(team) != 4:
        return [], []

    state_rules: list[models.StateRule] = []
    buff_rules: list[models.BuffRule] = []
    source_name = team[0].name
    counts = Counter(char.element for char in team)

    # 1. Fervent Flames (2+ Pyro): +25% ATK
    if counts["Pyro"] >= 2:
        buff_rules.append(
            models.BuffRule(
                buff_id="RESONANCE_PYRO_ATK",
                buff_name="Fervent Flames (Pyro Resonance) ATK%",
                character_source=source_name,
                stat="ATK%",
                base_value=0.25,
                target_scope="TEAM",
            )
        )

    # 2. Soothing Water (2+ Hydro): +25% Max HP
    if counts["Hydro"] >= 2:
        buff_rules.append(
            models.BuffRule(
                buff_id="RESONANCE_HYDRO_HP",
                buff_name="Soothing Water (Hydro Resonance) HP%",
                character_source=source_name,
                stat="HP%",
                base_value=0.25,
                target_scope="TEAM",
            )
        )

    # 3. Shattering Ice (2+ Cryo): +15% CRIT Rate vs Frozen or Cryo-affected enemies
    if counts["Cryo"] >= 2:
        buff_rules.append(
            models.BuffRule(
                buff_id="RESONANCE_CRYO_CR",
                buff_name="Shattering Ice (Cryo Resonance) Crit Rate",
                character_source=source_name,
                stat="Crit Rate",
                base_value=0.15,
                required_states=["ENEMY_AURA_CRYO_OR_FROZEN"],
                target_scope="TEAM",
            )
        )

    # 4. High Voltage (2+ Electro): Electro particle gen on Electro reactions (5s CD)
    if counts["Electro"] >= 2:
        for rxn in ("Superconduct", "Overloaded", "Electro-Charged", "Quicken", "Aggravate", "Hyperbloom", "Lunar-Charged"):
            state_rules.append(
                models.StateRule(
                    state_id="RESONANCE_ELECTRO_PARTICLE_CD",
                    base_duration=5.0,
                    character_source=source_name,
                    trigger_tags=["REACTION", rxn],
                    trigger_icd=5.0,
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="GLOBAL",
                    trigger_scope="TEAM",
                )
            )

    # 5. Sprawling Greenery (2+ Dendro):
    #    - Base +50 EM
    #    - +30 EM for 6s after Burning, Quicken, or Bloom/Lunar-Bloom
    #    - +20 EM for 6s after Aggravate, Spread, Hyperbloom, or Burgeon
    if counts["Dendro"] >= 2:
        buff_rules.append(
            models.BuffRule(
                buff_id="RESONANCE_DENDRO_BASE_EM",
                buff_name="Sprawling Greenery (Dendro Resonance) Base EM",
                character_source=source_name,
                stat="Elemental Mastery",
                base_value=50.0,
                target_scope="TEAM",
            )
        )
        for rxn in ("Burning", "Quicken", "Bloom", "Lunar-Bloom"):
            state_rules.append(
                models.StateRule(
                    state_id="RESONANCE_DENDRO_TIER1",
                    base_duration=6.0,
                    character_source=source_name,
                    trigger_tags=["REACTION", rxn],
                    trigger_icd=0.1,
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="GLOBAL",
                    trigger_scope="TEAM",
                )
            )
        for rxn in ("Aggravate", "Spread", "Hyperbloom", "Burgeon"):
            state_rules.append(
                models.StateRule(
                    state_id="RESONANCE_DENDRO_TIER2",
                    base_duration=6.0,
                    character_source=source_name,
                    trigger_tags=["REACTION", rxn],
                    trigger_icd=0.1,
                    max_stacks=1,
                    refresh_mode="REFRESH ALL",
                    target_scope="GLOBAL",
                    trigger_scope="TEAM",
                )
            )
        buff_rules.extend([
            models.BuffRule(
                buff_id="RESONANCE_DENDRO_TIER1_EM",
                buff_name="Sprawling Greenery (Primary Reaction) EM",
                character_source=source_name,
                stat="Elemental Mastery",
                base_value=30.0,
                required_states=["RESONANCE_DENDRO_TIER1"],
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="RESONANCE_DENDRO_TIER2_EM",
                buff_name="Sprawling Greenery (Secondary Reaction) EM",
                character_source=source_name,
                stat="Elemental Mastery",
                base_value=20.0,
                required_states=["RESONANCE_DENDRO_TIER2"],
                target_scope="TEAM",
            ),
        ])

    # 6. Enduring Rock (2+ Geo):
    #    - +15% Shield Strength
    #    - While shielded ("ANY:Shield" state): +15% DMG% and -20% Geo RES Shred for 15s on hit
    if counts["Geo"] >= 2:
        state_rules.append(
            models.StateRule(
                state_id="RESONANCE_GEO_SHRED",
                base_duration=15.0,
                character_source=source_name,
                trigger_tags=["HIT"],
                required_states=["ANY:Shield"],
                max_stacks=1,
                refresh_mode="REFRESH ALL",
                target_scope="GLOBAL",
                trigger_scope="TEAM",
            )
        )
        buff_rules.extend([
            models.BuffRule(
                buff_id="RESONANCE_GEO_SHIELD_STR",
                buff_name="Enduring Rock (Geo Resonance) Shield Strength",
                character_source=source_name,
                stat="Shield Strength",
                base_value=0.15,
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="RESONANCE_GEO_DMG",
                buff_name="Enduring Rock (Geo Resonance) Shielded DMG%",
                character_source=source_name,
                stat="All DMG%",
                base_value=0.15,
                required_states=["ANY:Shield"],
                target_scope="TEAM",
            ),
            models.BuffRule(
                buff_id="RESONANCE_GEO_RES_SHRED",
                buff_name="Enduring Rock (Geo Resonance) Geo RES Shred",
                character_source=source_name,
                stat="RES Shred",
                base_value=0.20,
                required_states=["RESONANCE_GEO_SHRED"],
                target_scope="TEAM",
                element_filters=["Geo"],
            ),
        ])

    # 7. Protective Canopy (4 Unique Elements): +15% All Elemental & Physical RES
    if len(counts) == 4:
        buff_rules.append(
            models.BuffRule(
                buff_id="RESONANCE_ALL_RES",
                buff_name="Protective Canopy All RES%",
                character_source=source_name,
                stat="All RES%",
                base_value=0.15,
                target_scope="TEAM",
            )
        )

    return state_rules, buff_rules