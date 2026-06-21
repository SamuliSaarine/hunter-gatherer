import { createSignal } from "solid-js";
import { store, addNarrativeEntry } from "../store/gameStore";
import { sendTurn } from "../api/ws";

export default function PlayerInput() {
  const [input, setInput] = createSignal("");
  let textareaRef: HTMLTextAreaElement | undefined;

  const canSubmit = () =>
    !store.isStreaming && store.isConnected && (store.gameState?.is_alive ?? false);

  const handleSubmit = () => {
    const text = input().trim();
    if (!text || !canSubmit()) return;
    addNarrativeEntry({ type: "player", text });
    sendTurn(text);
    setInput("");
    if (textareaRef) {
      textareaRef.style.height = "auto";
      textareaRef.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    // Desktop: Enter submits, Shift+Enter newline
    // Mobile: always show Send button, don't intercept Enter
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth >= 768) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: InputEvent) => {
    const el = e.currentTarget as HTMLTextAreaElement;
    setInput(el.value);
    // Auto-grow up to 5 lines
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  const placeholder = () => {
    if (!store.isConnected) return "Connecting...";
    if (store.isStreaming) return "...";
    if (store.gameState && !store.gameState.is_alive) return "Your story has ended.";
    if (!store.gameState) return "Start a new game first.";
    return "What do you do?";
  };

  return (
    <div class="player-input-wrapper">
      <textarea
        ref={textareaRef}
        class="player-input"
        value={input()}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        placeholder={placeholder()}
        disabled={!canSubmit()}
        rows={1}
        autofocus
      />
      <button
        class="send-btn"
        onClick={handleSubmit}
        disabled={!canSubmit() || !input().trim()}
        aria-label="Send"
      >
        ›
      </button>
    </div>
  );
}
