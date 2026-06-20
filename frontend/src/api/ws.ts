import {
  setStore,
  appendStreamChunk,
  finalizeStreamEntry,
  updateGameState,
  addNarrativeEntry,
} from "../store/gameStore";

let ws: WebSocket | null = null;

export function connectWebSocket(sessionId: string): WebSocket {
  if (ws) {
    ws.close();
  }

  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  const wsUrl = `${proto}//${host}/ws/${sessionId}`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    setStore("isConnected", true);
    setStore("sessionId", sessionId);
  };

  ws.onclose = () => {
    setStore("isConnected", false);
  };

  ws.onerror = () => {
    setStore("isConnected", false);
  };

  ws.onmessage = (event: MessageEvent) => {
    let message: any;
    try {
      message = JSON.parse(event.data as string);
    } catch {
      return;
    }

    switch (message.type) {
      case "stream_start":
        setStore("isStreaming", true);
        setStore("streamingText", "");
        break;

      case "chunk":
        appendStreamChunk(message.text as string);
        break;

      case "stream_end":
        finalizeStreamEntry();
        break;

      case "state_update":
        updateGameState(message.state);
        if (Array.isArray(message.npc_events)) {
          for (const event of message.npc_events as string[]) {
            addNarrativeEntry({ type: "event", text: event });
          }
        }
        if (message.died) {
          setStore("isDead", true);
          setStore("deathCause", message.death_cause as string | null);
          setStore("screen", "death");
          addNarrativeEntry({
            type: "death",
            text: `You have died: ${message.death_cause ?? "unknown cause"}`,
          });
        }
        break;

      case "error":
        addNarrativeEntry({
          type: "system",
          text: `Error: ${message.message as string}`,
        });
        break;

      case "dead":
        setStore("screen", "death");
        break;
    }
  };

  return ws;
}

export function sendTurn(playerInput: string): void {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "turn", input: playerInput }));
  }
}

export function disconnectWebSocket(): void {
  ws?.close();
  ws = null;
}
