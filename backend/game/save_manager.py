from pathlib import Path
from typing import Optional

from .state import GameState

SAVES_DIR = Path(__file__).parent.parent.parent / "saves"


def save_game(state: GameState) -> None:
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    path = SAVES_DIR / f"{state.session_id}.json"
    with open(path, "w") as f:
        f.write(state.model_dump_json(indent=2))


def load_game(session_id: str) -> Optional[GameState]:
    path = SAVES_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return GameState.model_validate_json(f.read())
    except (ValueError, IOError):
        return None


def list_saves() -> list[str]:
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in SAVES_DIR.glob("*.json") if p.stat().st_size > 0]
