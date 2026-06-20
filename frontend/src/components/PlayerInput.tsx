import { createSignal } from "solid-js";
import { store, addNarrativeEntry } from "../store/gameStore";
import { sendTurn } from "../api/ws";

export default function PlayerInput() {
  const [input, setInput] = createSignal("");

  const canSubmit = () =>
    !store.isStreaming && store.isConnected && (store.gameState?.is_alive ?? false);

  const handleSubmit = () => {
    const text = input().trim();
    if (!text || !canSubmit()) return;
    addNarrativeEntry({ type: "player", text });
    sendTurn(text);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const placeholder = () => {
    if (!store.isConnected) return "Connecting to server...";
    if (store.isStreaming) return "...";
    if (store.gameState && !store.gameState.is_alive) return "Your story has ended.";
    if (!store.gameState) return "Start a new game to begin.";
    return "What do you do? (Enter to act)";
  };

  return (
    <div class="player-input-wrapper">
      <span class="input-prompt">›</span>
      <textarea
        class="player-input"
        value={input()}
        onInput={(e) => setInput(e.currentTarget.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder()}
        disabled={!canSubmit()}
        rows={2}
        autofocus
      />
    </div>
  );
}
