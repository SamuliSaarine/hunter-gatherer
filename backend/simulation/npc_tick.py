import random
from game.state import GameState, Character


def run_npc_tick(state: GameState) -> tuple[GameState, list[str]]:
    events: list[str] = []
    player = next((c for c in state.characters if c.is_player), None)
    player_zone = player.current_zone_id if player else "camp"

    for char in state.characters:
        if char.is_player or not char.is_alive:
            continue

        # Passive aging — very slow
        if state.current_day == 1 and state.current_season.value == "spring":
            char.age += 1

        # Simple autonomous behavior
        if char.hunger < 40:
            # Go hunting/gathering
            char.hunger = min(100, char.hunger + 15)
            char.fatigue = min(100, char.fatigue + 10)
            if char.current_zone_id == player_zone:
                events.append(f"{char.name} slips away to find food.")
        elif char.fatigue > 70:
            # Rest
            char.fatigue = max(0, char.fatigue - 20)
        else:
            # Gossip — affects player reputation slightly
            if char.current_zone_id == player_zone and player:
                delta = random.uniform(-2, 3)
                player.reputation = max(0, min(100, player.reputation + delta))
                if abs(delta) > 1.5:
                    direction = "warmly" if delta > 0 else "cautiously"
                    events.append(f"{char.name} speaks {direction} of you near the fire.")

        # Passive hunger decay for NPCs
        char.hunger = max(0, char.hunger - 2)

    return state, events
