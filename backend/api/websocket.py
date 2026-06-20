import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from game.engine import pre_turn_tick, apply_gm_response, check_and_handle_death
from game.save_manager import save_game
from ai.gm_agent import stream_gm_narrative, get_gm_delta
from .routes import _sessions

ws_router = APIRouter()


@ws_router.websocket("/ws/{session_id}")
async def websocket_turn(websocket: WebSocket, session_id: str) -> None:
    secret = os.environ.get("GAME_SECRET", "")
    if secret and websocket.cookies.get("game_session") != secret:
        await websocket.close(code=4001)
        return
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue

            if message.get("type") != "turn":
                continue

            player_input = message.get("input", "").strip()
            if not player_input:
                continue

            state = _sessions.get(session_id)
            if not state:
                await websocket.send_json({"type": "error", "message": "Session not found. Please reload."})
                continue

            if not state.is_alive:
                await websocket.send_json({"type": "dead", "message": "Your story has ended."})
                continue

            # Pre-turn world tick
            state, npc_events = pre_turn_tick(state)
            state.current_turn += 1

            # Stream GM narrative
            full_narrative = ""
            await websocket.send_json({"type": "stream_start"})

            async for chunk in stream_gm_narrative(state, player_input):
                full_narrative += chunk
                await websocket.send_json({"type": "chunk", "text": chunk})

            await websocket.send_json({"type": "stream_end"})

            # Get structured delta from narrative
            gm_response = await get_gm_delta(state, player_input, full_narrative)

            # Apply delta
            state = apply_gm_response(state, gm_response)

            # Permadeath check
            state, died, cause = check_and_handle_death(state)

            # Persist
            _sessions[session_id] = state
            if state.is_alive:
                save_game(state)

            # Send final state update
            await websocket.send_json({
                "type": "state_update",
                "state": state.model_dump(),
                "died": died,
                "death_cause": cause,
                "npc_events": npc_events,
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
