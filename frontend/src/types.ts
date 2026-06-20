export type Season = "spring" | "summer" | "autumn" | "winter";

export interface Character {
  id: string;
  name: string;
  age: number;
  is_player: boolean;
  is_alive: boolean;
  health: number;
  hunger: number;
  fatigue: number;
  reputation: number;
  strength: number;
  endurance: number;
  perception: number;
  language: number;
  abstraction: number;
  memory: number;
  believed_fiction_ids: string[];
  skills: Record<string, number>;
  personality: string;
  current_zone_id: string;
  cause_of_death?: string;
}

export interface SharedFiction {
  id: string;
  name: string;
  fiction_type: string;
  narrative: string;
  believer_ids: string[];
  belief_strength: number;
  status: string;
  origin_character_id: string;
}

export interface Zone {
  id: string;
  name: string;
  zone_type: string;
  resources: Record<string, number>;
  danger_level: number;
  connected_zone_ids: string[];
  description: string;
}

export interface Band {
  id: string;
  name: string;
  member_ids: string[];
  current_zone_id: string;
  dominant_fiction_ids: string[];
  belief_cohesion: number;
  internal_tension: number;
  shared_food: number;
}

export interface GameState {
  version: string;
  session_id: string;
  current_turn: number;
  current_day: number;
  current_season: Season;
  current_year: number;
  world_zones: Zone[];
  band: Band;
  player_id: string;
  characters: Character[];
  shared_fictions: SharedFiction[];
  recent_events: string[];
  permadeath_enabled: boolean;
  difficulty: string;
  is_alive: boolean;
}

export interface NarrativeEntry {
  id: string;
  type: "player" | "gm" | "event" | "death" | "system";
  text: string;
  turn?: number;
}
