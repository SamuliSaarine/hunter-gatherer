import os
from typing import AsyncGenerator

from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

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
- 2-4 paragraphs. End when the scene settles. Be honest about failure."""

DELTA_SYSTEM_PROMPT = """You are a game state parser for a hunter-gatherer RPG.
Given what the player did and the narrative of what happened, return the structured state delta.
Use exact IDs from the provided maps. Use empty lists when nothing changed.
Only set death_occurred=true for actual character death."""


def _narrative_agent() -> Agent[None, str]:
    return Agent(
        MistralModel("mistral-large-latest", api_key=os.environ.get("MISTRAL_API_KEY")),
        system_prompt=GM_SYSTEM_PROMPT,
        result_type=str,
    )


def _delta_agent() -> Agent[None, GMResponse]:
    return Agent(
        MistralModel("mistral-small-latest", api_key=os.environ.get("MISTRAL_API_KEY")),
        system_prompt=DELTA_SYSTEM_PROMPT,
        result_type=GMResponse,
    )


async def stream_gm_narrative(
    state: GameState,
    player_input: str,
) -> AsyncGenerator[str, None]:
    context = build_context(state)
    async with _narrative_agent().run_stream(
        f"{context}\n\nPLAYER: {player_input}"
    ) as result:
        async for chunk in result.stream_text(delta=True):
            yield chunk


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
{narrative}"""

    result = await _delta_agent().run(prompt)
    return result.data
