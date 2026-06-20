from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import uuid


class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class Character(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    is_player: bool = False
    is_alive: bool = True
    health: float = Field(default=100.0, ge=0, le=100)
    hunger: float = Field(default=80.0, ge=0, le=100)
    fatigue: float = Field(default=20.0, ge=0, le=100)
    reputation: float = Field(default=50.0, ge=0, le=100)
    strength: int = Field(default=10, ge=1, le=20)
    endurance: int = Field(default=10, ge=1, le=20)
    perception: int = Field(default=10, ge=1, le=20)
    language: int = Field(default=10, ge=1, le=20)
    abstraction: int = Field(default=8, ge=1, le=20)
    memory: int = Field(default=10, ge=1, le=20)
    believed_fiction_ids: list[str] = Field(default_factory=list)
    skills: dict[str, int] = Field(default_factory=dict)
    personality: str = ""
    current_zone_id: str = "camp"
    cause_of_death: Optional[str] = None


class SharedFiction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    fiction_type: str  # myth | ritual | taboo | totem | ancestor_cult
    narrative: str
    believer_ids: list[str] = Field(default_factory=list)
    belief_strength: float = Field(default=70.0, ge=0, le=100)
    spread_rate: float = Field(default=0.1, ge=0, le=1)
    status: str = "dominant"  # emerging | dominant | contested | declining | dead
    origin_character_id: str = ""


class Zone(BaseModel):
    id: str
    name: str
    zone_type: str  # camp | forest | plains | river | hills | cave | sacred_ground
    resources: dict[str, float] = Field(default_factory=dict)
    danger_level: float = Field(default=0.1, ge=0, le=1)
    connected_zone_ids: list[str] = Field(default_factory=list)
    description: str


class Band(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    member_ids: list[str] = Field(default_factory=list)
    current_zone_id: str = "camp"
    dominant_fiction_ids: list[str] = Field(default_factory=list)
    belief_cohesion: float = Field(default=75.0, ge=0, le=100)
    internal_tension: float = Field(default=20.0, ge=0, le=100)
    shared_food: float = Field(default=50.0, ge=0)


class GameState(BaseModel):
    version: str = "0.1.0"
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_turn: int = 0
    current_day: int = 1
    current_season: Season = Season.SPRING
    current_year: int = 1
    world_zones: list[Zone] = Field(default_factory=list)
    band: Band
    player_id: str
    characters: list[Character] = Field(default_factory=list)
    shared_fictions: list[SharedFiction] = Field(default_factory=list)
    recent_events: list[str] = Field(default_factory=list)
    permadeath_enabled: bool = True
    difficulty: str = "normal"
    is_alive: bool = True


# Delta models for GM structured output
class StatDelta(BaseModel):
    character_id: str
    health_delta: float = 0
    hunger_delta: float = 0
    fatigue_delta: float = 0
    reputation_delta: float = 0
    skill_changes: dict[str, int] = Field(default_factory=dict)


class RelationshipDelta(BaseModel):
    from_id: str
    to_id: str
    trust_delta: int  # -10 to +10


class FictionDelta(BaseModel):
    fiction_id: Optional[str] = None  # None = new fiction
    action: str  # strengthen | weaken | spread_to | destroy | create
    target_believer_ids: list[str] = Field(default_factory=list)
    belief_strength_delta: float = 0
    new_fiction_name: Optional[str] = None
    new_fiction_narrative: Optional[str] = None
    new_fiction_type: Optional[str] = None


class ZoneDelta(BaseModel):
    character_id: str
    new_zone_id: str


class ResourceDelta(BaseModel):
    zone_id: Optional[str] = None  # None = band shared food
    resource: str
    delta: float


class GMResponse(BaseModel):
    narrative: str
    stat_deltas: list[StatDelta] = Field(default_factory=list)
    relationship_deltas: list[RelationshipDelta] = Field(default_factory=list)
    fiction_deltas: list[FictionDelta] = Field(default_factory=list)
    zone_deltas: list[ZoneDelta] = Field(default_factory=list)
    resource_deltas: list[ResourceDelta] = Field(default_factory=list)
    new_event: Optional[str] = None
    death_occurred: bool = False
    death_character_id: Optional[str] = None
    death_cause: Optional[str] = None
