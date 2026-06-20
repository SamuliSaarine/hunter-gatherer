import { For, Show, createEffect } from "solid-js";
import { store } from "../store/gameStore";
import type { NarrativeEntry } from "../types";

function entryClass(type: NarrativeEntry["type"]): string {
  const base = "entry";
  if (type === "player") return `${base} player-entry`;
  if (type === "event") return `${base} event-entry`;
  if (type === "death") return `${base} death-entry`;
  if (type === "system") return `${base} system-entry`;
  return `${base} gm-entry`;
}

function entryPrefix(type: NarrativeEntry["type"]): string {
  if (type === "player") return "> ";
  if (type === "event") return "~ ";
  if (type === "death") return "✦ ";
  return "";
}

export default function NarrativeScroll() {
  let scrollRef: HTMLDivElement | undefined;

  const scrollToBottom = () => {
    if (scrollRef) {
      scrollRef.scrollTop = scrollRef.scrollHeight;
    }
  };

  createEffect(() => {
    void store.narrative.length;
    void store.streamingText;
    scrollToBottom();
  });

  return (
    <div class="narrative-scroll" ref={scrollRef}>
      <Show when={!store.gameState}>
        <div class="narrative-placeholder">
          <div class="title-art">HUNTER-GATHERER</div>
          <div class="subtitle dim">Natural language RPG · Pleistocene band life</div>
          <div class="subtitle dim">Based on Harari's Sapiens</div>
        </div>
      </Show>

      <For each={store.narrative}>
        {(entry) => (
          <div class={entryClass(entry.type)}>
            <span class="entry-prefix">{entryPrefix(entry.type)}</span>
            <span class="entry-text">{entry.text}</span>
          </div>
        )}
      </For>

      <Show when={store.isStreaming || store.streamingText}>
        <div class="entry gm-entry streaming">
          <span class="entry-text">{store.streamingText}</span>
          <span class="cursor">▋</span>
        </div>
      </Show>
    </div>
  );
}
