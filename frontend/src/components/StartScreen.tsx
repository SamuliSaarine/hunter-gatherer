import { createSignal, For, Show, createResource } from "solid-js";
import { createNewGame, listSaves, loadGame, getLegacy } from "../api/client";
import { setStore, updateGameState, addNarrativeEntry } from "../store/gameStore";
import { connectWebSocket } from "../api/ws";

export default function StartScreen() {
  const [playerName, setPlayerName] = createSignal("");
  const [difficulty, setDifficulty] = createSignal("normal");
  const [error, setError] = createSignal("");
  const [loading, setLoading] = createSignal(false);

  const [saves] = createResource<string[]>(listSaves);
  const [legacy] = createResource<any[]>(getLegacy);

  const startNewGame = async () => {
    const name = playerName().trim();
    if (!name) {
      setError("Enter your name to begin.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const state = await createNewGame(name, difficulty());
      updateGameState(state);
      connectWebSocket(state.session_id);
      addNarrativeEntry({
        type: "system",
        text: `You are ${name}. The Ochre Clan makes camp at the river bend as spring begins.`,
      });
      setStore("screen", "game");
    } catch (e) {
      setError("Failed to connect. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  const resumeGame = async (sessionId: string) => {
    setLoading(true);
    setError("");
    try {
      const state = await loadGame(sessionId);
      updateGameState(state);
      connectWebSocket(state.session_id);
      addNarrativeEntry({
        type: "system",
        text: `Resuming — ${state.band.name}, ${state.current_season} of Year ${state.current_year}.`,
      });
      setStore("screen", "game");
    } catch {
      setError("Failed to load save.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="start-screen">
      <div class="start-title">HUNTER-GATHERER</div>
      <div class="start-subtitle">A natural language RPG</div>
      <div class="start-tagline dim">
        Pleistocene band life · Shared myths · Permadeath
      </div>

      <div class="start-form">
        <input
          class="start-input"
          type="text"
          placeholder="Your name"
          value={playerName()}
          onInput={(e) => setPlayerName(e.currentTarget.value)}
          onKeyDown={(e) => e.key === "Enter" && startNewGame()}
          autofocus
        />

        <div class="difficulty-row">
          <For each={["normal", "harsh", "brutal"] as const}>
            {(d) => (
              <button
                class={`diff-btn ${difficulty() === d ? "active" : ""}`}
                onClick={() => setDifficulty(d)}
              >
                {d.toUpperCase()}
              </button>
            )}
          </For>
        </div>

        <button class="start-btn" onClick={startNewGame} disabled={loading()}>
          {loading() ? "Starting..." : "Begin"}
        </button>

        <Show when={error()}>
          <div class="error-msg">{error()}</div>
        </Show>
      </div>

      <Show when={(saves()?.length ?? 0) > 0}>
        <div class="saves-section">
          <div class="saves-title">CONTINUE</div>
          <For each={saves()}>
            {(id) => (
              <button class="save-btn" onClick={() => resumeGame(id)}>
                {id.slice(0, 8)}...
              </button>
            )}
          </For>
        </div>
      </Show>

      <Show when={(legacy()?.length ?? 0) > 0}>
        <div class="legacy-section">
          <div class="saves-title">HALL OF THE ANCESTORS</div>
          <For each={legacy()}>
            {(entry) => (
              <div class="legacy-entry dim">
                {entry.name}, age {entry.age} —{" "}
                {entry.cause_of_death} in {entry.season}, Year {entry.year}
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
}
