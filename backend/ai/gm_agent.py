import json
import os
from typing import AsyncGenerator

from openai import AsyncOpenAI

from game.state import GameState, GMResponse
from .context_builder import build_context

GM_SYSTEM_PROMPT = """You are the Game Master of Hunter-Gatherer, a hardcore natural-language RPG.

SETTING: A Pleistocene hunter-gatherer band of ~50 people, roughly 70,000 BCE.
The player types anything in natural language. You interpret and resolve it.

HARARI'S RULES (these are physics, not flavor):
- Shared myths hold the band together. When belief_cohesion drops below 30, the band fractures.
- Reputation is survival. exile = death in the Pleistocene.
- Nothing is free. Every action costs calories, social capital, or cognitive energy.
- NPCs believe their myths are literally true. They are fully human, not primitive.
- The player has no special status. The band will exile, shun, or kill them.
- The world is not fair. Disease, predators, and weather kill without warning.

YOUR ROLE:
- Interpret the player's natural language and resolve it against the world state
- Voice all NPCs naturally in the narrative — their speech, their hesitations, their reactions
- Apply realistic consequences: physical, social, ecological
- Show the world as alive: weather changes, animals move, NPCs have their own concerns
- In "brutal" difficulty: never suggest what the player should do next
- Write vivid, anthropologically grounded prose. No anachronisms. No magic.
- 2-4 paragraphs. End when the scene settles. Be honest about failure.
- If the player does something unclear, interpret it charitably but realistically."""

DELTA_SYSTEM_PROMPT = """You are a game state parser. Given a narrative of what happened in a hunter-gatherer RPG, output ONLY a valid JSON object with state changes. No markdown. No explanation. Just JSON.

Use exact character/fiction/zone IDs from the provided map. Use empty arrays when nothing changed.

Schema:
{
  "narrative": "copy the full narrative here",
  "stat_deltas": [{"character_id": "<exact_id>", "health_delta": 0.0, "hunger_delta": 0.0, "fatigue_delta": 0.0, "reputation_delta": 0.0, "skill_changes": {}}],
  "relationship_deltas": [{"from_id": "<id>", "to_id": "<id>", "trust_delta": 0}],
  "fiction_deltas": [{"fiction_id": "<id_or_null>", "action": "strengthen|weaken|spread_to|destroy|create", "target_believer_ids": [], "belief_strength_delta": 0.0, "new_fiction_name": null, "new_fiction_narrative": null, "new_fiction_type": null}],
  "zone_deltas": [{"character_id": "<id>", "new_zone_id": "<zone_id>"}],
  "resource_deltas": [{"zone_id": "<zone_id_or_null>", "resource": "food|wood|stone|medicine|hides", "delta": 0.0}],
  "new_event": "one-line past-tense summary",
  "death_occurred": false,
  "death_character_id": null,
  "death_cause": null
}

Rules:
- hunger_delta: negative when player expends energy (hunting=-15 to -25), positive when eating (+20 to +40)
- health_delta: only when injured or healed
- reputation_delta: social actions change this (-20 to +20 range)
- fatigue_delta: positive when resting, negative when exerting (-10 to -20)
- Always include the narrative field with the full text
- Set death_occurred=true only for actual character death"""

_MISTRAL_BASE_URL = "https://api.mistral.ai/v1"


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ.get("MISTRAL_API_KEY"),
        base_url=_MISTRAL_BASE_URL,
    )


async def stream_gm_narrative(
    state: GameState,
    player_input: str,
) -> AsyncGenerator[str, None]:
    context = build_context(state)
    stream = await _client().chat.completions.create(
        model="mistral-large-latest",
        max_tokens=1200,
        stream=True,
        messages=[
            {"role": "system", "content": GM_SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}\n\nPLAYER: {player_input}"},
        ],
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


async def get_gm_delta(
    state: GameState,
    player_input: str,
    narrative: str,
) -> GMResponse:
    char_map = "\n".join(f"  {c.id}: {c.name} (player={c.is_player})" for c in state.characters)
    fiction_map = "\n".join(f"  {f.id}: {f.name}" for f in state.shared_fictions)
    zone_map = "\n".join(f"  {z.id}: {z.name}" for z in state.world_zones)

    prompt = f"""CHARACTER IDs:
{char_map}
FICTION IDs:
{fiction_map}
ZONE IDs:
{zone_map}
PLAYER_ID: {state.player_id}

WHAT PLAYER DID: {player_input}

NARRATIVE (what happened):
{narrative}

Output the JSON delta."""

    response = await _client().chat.completions.create(
        model="mistral-small-latest",
        max_tokens=800,
        messages=[
            {"role": "system", "content": DELTA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    try:
        data = json.loads(raw)
        return GMResponse(**data)
    except Exception:
        return GMResponse(narrative=narrative, new_event=f"Turn {state.current_turn}")
