from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth import require_auth

from game.state import GameState, Band, Character, SharedFiction
from game.save_manager import save_game, load_game, list_saves
from game.permadeath import get_legacy
from world.zones import create_starting_world
from simulation.relationships import initialize_relationships

router = APIRouter(prefix="/api", dependencies=[Depends(require_auth)])

# In-memory session store
_sessions: dict[str, GameState] = {}


class NewGameRequest(BaseModel):
    player_name: str
    difficulty: str = "normal"


class LoadGameRequest(BaseModel):
    session_id: str


def create_starting_npcs() -> list[Character]:
    npcs_data = [
        {"name": "Mara", "age": 58, "personality": "wise elder, keeper of stories; invented the River Taboo 30 seasons ago to avoid conflict", "strength": 7, "endurance": 8, "perception": 16, "language": 18, "abstraction": 15, "memory": 19, "health": 82.0, "hunger": 70.0},
        {"name": "Kael", "age": 28, "personality": "skilled hunter, proud and competitive; secretly doubts the Ancestor Spirits", "strength": 16, "endurance": 15, "perception": 14, "language": 9, "abstraction": 7, "memory": 10, "health": 95.0, "hunger": 60.0},
        {"name": "Yssa", "age": 34, "personality": "healer and midwife, pragmatic and deeply devout, protective of the young", "strength": 9, "endurance": 13, "perception": 15, "language": 14, "abstraction": 12, "memory": 16, "health": 90.0, "hunger": 75.0},
        {"name": "Bonn", "age": 19, "personality": "reckless young man eager to prove himself; follows Kael everywhere", "strength": 14, "endurance": 13, "perception": 11, "language": 8, "abstraction": 6, "memory": 9, "health": 98.0, "hunger": 55.0},
        {"name": "Sere", "age": 45, "personality": "quiet craftsman who makes the best tools; says little but misses nothing", "strength": 12, "endurance": 11, "perception": 17, "language": 7, "abstraction": 10, "memory": 14, "health": 88.0, "hunger": 68.0},
        {"name": "Litha", "age": 31, "personality": "mother of two, fierce and funny; hub of the band's gossip network", "strength": 10, "endurance": 12, "perception": 13, "language": 16, "abstraction": 9, "memory": 13, "health": 92.0, "hunger": 72.0},
        {"name": "Orm", "age": 67, "personality": "ancient, nearly blind, but his stories are the band's living memory", "strength": 5, "endurance": 6, "perception": 8, "language": 17, "abstraction": 16, "memory": 20, "health": 65.0, "hunger": 60.0},
        {"name": "Pell", "age": 14, "personality": "curious girl who watches everything and asks uncomfortable questions", "strength": 6, "endurance": 10, "perception": 18, "language": 11, "abstraction": 13, "memory": 15, "health": 100.0, "hunger": 80.0},
    ]

    return [
        Character(
            name=d["name"],
            age=d["age"],
            personality=d["personality"],
            is_player=False,
            health=d["health"],
            hunger=d["hunger"],
            fatigue=15.0,
            reputation=50.0,
            strength=d["strength"],
            endurance=d["endurance"],
            perception=d["perception"],
            language=d["language"],
            abstraction=d["abstraction"],
            memory=d["memory"],
            current_zone_id="camp",
        )
        for d in npcs_data
    ]


@router.post("/game/new")
async def new_game(request: NewGameRequest) -> GameState:
    zones = create_starting_world()

    player = Character(
        name=request.player_name,
        age=22,
        is_player=True,
        health=100.0,
        hunger=75.0,
        fatigue=15.0,
        reputation=50.0,
        strength=12,
        endurance=11,
        perception=13,
        language=10,
        abstraction=8,
        memory=10,
        current_zone_id="camp",
    )

    npcs = create_starting_npcs()
    all_chars = [player] + npcs

    ancestor_myth = SharedFiction(
        name="The Ancestors Watch",
        fiction_type="ancestor_cult",
        narrative=(
            "The spirits of our ancestors walk beside us always. "
            "They see every act of generosity and every act of greed. "
            "To hoard is to invite their wrath; to share is to earn their blessing."
        ),
        believer_ids=[c.id for c in all_chars],
        belief_strength=80.0,
        spread_rate=0.05,
        status="dominant",
        origin_character_id=npcs[0].id,
    )

    band = Band(
        name="The Ochre Clan",
        member_ids=[c.id for c in all_chars],
        current_zone_id="camp",
        dominant_fiction_ids=[ancestor_myth.id],
        belief_cohesion=75.0,
        internal_tension=20.0,
        shared_food=60.0,
    )

    state = GameState(
        world_zones=zones,
        band=band,
        player_id=player.id,
        characters=all_chars,
        shared_fictions=[ancestor_myth],
        permadeath_enabled=True,
        difficulty=request.difficulty,
        recent_events=["The Ochre Clan makes camp at the river bend as spring begins."],
    )

    initialize_relationships(all_chars)

    _sessions[state.session_id] = state
    save_game(state)
    return state


@router.get("/game/state/{session_id}")
async def get_state(session_id: str) -> GameState:
    if session_id in _sessions:
        return _sessions[session_id]
    state = load_game(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    _sessions[session_id] = state
    return state


@router.post("/game/load")
async def load_game_session(request: LoadGameRequest) -> GameState:
    state = load_game(request.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Save not found")
    _sessions[state.session_id] = state
    return state


@router.get("/game/saves")
async def list_game_saves() -> list[str]:
    return list_saves()


@router.get("/legacy")
async def get_legacy_records() -> list[dict]:
    return get_legacy()
