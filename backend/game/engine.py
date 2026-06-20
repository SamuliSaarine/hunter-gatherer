from typing import Optional

from .state import GameState, GMResponse, FictionDelta
from world.biome import apply_seasonal_tick
from world.time_keeper import advance_time
from simulation.npc_tick import run_npc_tick
from simulation.shared_fiction import apply_belief_tick, apply_fiction_delta
from game.permadeath import check_death_conditions, record_death


def apply_gm_response(state: GameState, response: GMResponse) -> GameState:
    # Stat deltas
    for delta in response.stat_deltas:
        for char in state.characters:
            if char.id == delta.character_id:
                char.health = max(0.0, min(100.0, char.health + delta.health_delta))
                char.hunger = max(0.0, min(100.0, char.hunger + delta.hunger_delta))
                char.fatigue = max(0.0, min(100.0, char.fatigue + delta.fatigue_delta))
                char.reputation = max(0.0, min(100.0, char.reputation + delta.reputation_delta))
                for skill, change in delta.skill_changes.items():
                    char.skills[skill] = max(0, min(100, char.skills.get(skill, 0) + change))

    # Zone deltas (movement)
    zone_ids = {z.id for z in state.world_zones}
    for delta in response.zone_deltas:
        if delta.new_zone_id not in zone_ids:
            continue
        for char in state.characters:
            if char.id == delta.character_id:
                char.current_zone_id = delta.new_zone_id
                if char.is_player:
                    state.band.current_zone_id = delta.new_zone_id

    # Resource deltas
    for delta in response.resource_deltas:
        if delta.zone_id is None:
            state.band.shared_food = max(0.0, state.band.shared_food + delta.delta)
        else:
            for zone in state.world_zones:
                if zone.id == delta.zone_id:
                    zone.resources[delta.resource] = max(
                        0.0, zone.resources.get(delta.resource, 0.0) + delta.delta
                    )

    # Fiction deltas
    for fdelta in response.fiction_deltas:
        state.shared_fictions, state.characters = apply_fiction_delta(
            state.shared_fictions, state.characters, fdelta
        )

    # New event
    if response.new_event:
        state.recent_events.append(response.new_event)
        if len(state.recent_events) > 20:
            state.recent_events = state.recent_events[-20:]

    return state


def pre_turn_tick(state: GameState) -> tuple[GameState, list[str]]:
    state = advance_time(state)

    # Seasonal resource tick at start of each new season
    if state.current_day == 1:
        state.world_zones = apply_seasonal_tick(state.world_zones, state.current_season)

    # Passive player hunger decay (3 per day)
    player = next((c for c in state.characters if c.is_player), None)
    if player:
        player.hunger = max(0.0, player.hunger - 3.0)
        # Slight natural fatigue recovery
        player.fatigue = max(0.0, player.fatigue - 2.0)

    # NPC autonomous actions
    state, npc_events = run_npc_tick(state)

    # Belief drift
    state.shared_fictions = apply_belief_tick(state.shared_fictions, state.characters)

    # Band cohesion based on dominant fiction strength
    dominant_fictions = [
        f for f in state.shared_fictions
        if f.id in state.band.dominant_fiction_ids and f.status != "dead"
    ]
    if dominant_fictions:
        avg_strength = sum(f.belief_strength for f in dominant_fictions) / len(dominant_fictions)
        state.band.belief_cohesion = min(100.0, max(0.0,
            state.band.belief_cohesion * 0.95 + avg_strength * 0.05
        ))

    return state, npc_events


def check_and_handle_death(
    state: GameState,
) -> tuple[GameState, bool, Optional[str]]:
    is_dead, char_id, cause = check_death_conditions(state)
    if is_dead and char_id and cause:
        record_death(state, char_id, cause)
        for char in state.characters:
            if char.id == char_id:
                char.is_alive = False
                char.cause_of_death = cause
        state.is_alive = False
        return state, True, cause
    return state, False, None
