import { createStore } from "solid-js/store";
import type { GameState, NarrativeEntry } from "../types";

export type Screen = "start" | "game" | "death";

interface GameStore {
  gameState: GameState | null;
  sessionId: string | null;
  narrative: NarrativeEntry[];
  streamingText: string;
  isStreaming: boolean;
  isConnected: boolean;
  isDead: boolean;
  deathCause: string | null;
  screen: Screen;
}

const [store, setStore] = createStore<GameStore>({
  gameState: null,
  sessionId: null,
  narrative: [],
  streamingText: "",
  isStreaming: false,
  isConnected: false,
  isDead: false,
  deathCause: null,
  screen: "start",
});

export { store, setStore };

export function addNarrativeEntry(entry: Omit<NarrativeEntry, "id">): void {
  setStore("narrative", (prev) => [
    ...prev,
    { ...entry, id: crypto.randomUUID() },
  ]);
}

export function appendStreamChunk(chunk: string): void {
  setStore("streamingText", (prev) => prev + chunk);
}

export function finalizeStreamEntry(): void {
  const text = store.streamingText;
  if (text.trim()) {
    addNarrativeEntry({ type: "gm", text });
  }
  setStore("streamingText", "");
  setStore("isStreaming", false);
}

export function updateGameState(state: GameState): void {
  setStore("gameState", state);
  setStore("sessionId", state.session_id);
}
