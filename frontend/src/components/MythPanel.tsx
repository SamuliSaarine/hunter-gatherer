import { For, Show } from "solid-js";
import { store } from "../store/gameStore";
import type { SharedFiction } from "../types";

function statusColor(status: string): string {
  if (status === "dominant") return "var(--green)";
  if (status === "contested") return "var(--yellow)";
  if (status === "declining") return "var(--red)";
  if (status === "emerging") return "var(--amber)";
  return "var(--dim)";
}

export default function MythPanel() {
  const activeFictions = (): SharedFiction[] =>
    store.gameState?.shared_fictions.filter((f) => f.status !== "dead") ?? [];

  return (
    <div class="panel myth-panel">
      <div class="panel-title">SHARED MYTHS</div>
      <Show
        when={activeFictions().length > 0}
        fallback={<div class="dim">No myths</div>}
      >
        <For each={activeFictions()}>
          {(fiction) => (
            <div class="fiction-row">
              <div class="fiction-name" style={{ color: statusColor(fiction.status) }}>
                {fiction.name}
              </div>
              <div class="fiction-bar-row">
                <div class="stat-bar-track fiction-bar">
                  <div
                    class="stat-bar-fill"
                    style={{
                      width: `${fiction.belief_strength}%`,
                      "background-color": statusColor(fiction.status),
                    }}
                  />
                </div>
                <span class="fiction-val dim">{Math.round(fiction.belief_strength)}</span>
              </div>
              <div class="fiction-type dim">{fiction.fiction_type}</div>
            </div>
          )}
        </For>
      </Show>
    </div>
  );
}
