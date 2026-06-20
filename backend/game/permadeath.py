import json
import random
from pathlib import Path
from typing import Optional

from .state import GameState

LEGACY_FILE = Path(__file__).parent.parent.parent / "data" / "legacy.json"
SAVES_DIR = Path(__file__).parent.parent.parent / "saves"


def check_death_conditions(state: GameState) -> tuple[bool, Optional[str], Optional[str]]:
    player = next((c for c in state.characters if c.is_player and c.is_alive), None)
    if not player:
        return False, None, None

    if player.health <= 0:
        return True, player.id, "wounds"

    if player.hunger <= 0:
        return True, player.id, "starvation"

    if player.reputation <= 5 and state.band.internal_tension > 75:
        return True, player.id, "exile — cast out from the band into the wilderness"

    if player.age >= 50:
        death_chance = (player.age - 50) * 0.04
        if random.random() < death_chance / DAYS_PER_YEAR:
            return True, player.id, "old age — your body finally refused"

    return False, None, None


DAYS_PER_YEAR = 120  # 30 days * 4 seasons


def record_death(state: GameState, character_id: str, cause: str) -> None:
    player = next((c for c in state.characters if c.id == character_id), None)
    if not player:
        return

    LEGACY_FILE.parent.mkdir(parents=True, exist_ok=True)

    legacy: list[dict] = []
    if LEGACY_FILE.exists():
        try:
            with open(LEGACY_FILE) as f:
                legacy = json.load(f)
        except (json.JSONDecodeError, IOError):
            legacy = []

    legacy.append({
        "name": player.name,
        "age": player.age,
        "cause_of_death": cause,
        "band_name": state.band.name,
        "season": state.current_season.value,
        "year": state.current_year,
        "day": state.current_day,
        "turn": state.current_turn,
        "last_zone": player.current_zone_id,
        "reputation": round(player.reputation),
        "health": round(player.health),
    })

    with open(LEGACY_FILE, "w") as f:
        json.dump(legacy, f, indent=2)

    save_file = SAVES_DIR / f"{state.session_id}.json"
    if save_file.exists():
        save_file.unlink()


def get_legacy() -> list[dict]:
    if not LEGACY_FILE.exists():
        return []
    try:
        with open(LEGACY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
