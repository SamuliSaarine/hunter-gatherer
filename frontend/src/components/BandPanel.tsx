import { For, Show } from "solid-js";
import { store } from "../store/gameStore";
import type { Character } from "../types";

function extractRole(personality: string): string {
  const p = personality.toLowerCase();
  if (p.includes("elder")) return "elder";
  if (p.includes("hunter")) return "hunter";
  if (p.includes("healer")) return "healer";
  if (p.includes("craftsman")) return "craftsman";
  if (p.includes("mother")) return "mother";
  if (p.includes("ancient") || p.includes("blind")) return "ancient";
  if (p.includes("girl") || p.includes("curious")) return "child";
  return "member";
}

export default function BandPanel() {
  const player = (): Character | undefined =>
    store.gameState?.characters.find((c) => c.is_player);

  const nearbyNpcs = (): Character[] => {
    const zone = player()?.current_zone_id;
    return (
      store.gameState?.characters.filter(
        (c) => !c.is_player && c.is_alive && c.current_zone_id === zone
      ) ?? []
    );
  };

  const elsewhereCount = (): number => {
    const zone = player()?.current_zone_id;
    return (
      store.gameState?.characters.filter(
        (c) => !c.is_player && c.is_alive && c.current_zone_id !== zone
      ).length ?? 0
    );
  };

  return (
    <div class="panel band-panel">
      <div class="panel-title">BAND · {store.gameState?.band.name ?? "—"}</div>
      <Show
        when={nearbyNpcs().length > 0}
        fallback={<div class="dim">No one nearby</div>}
      >
        <For each={nearbyNpcs()}>
          {(npc) => (
            <div class="npc-row">
              <span class="npc-name">{npc.name}</span>
              <span class="npc-age dim">{npc.age}</span>
              <span class="npc-role dim">{extractRole(npc.personality)}</span>
            </div>
          )}
        </For>
      </Show>
      <Show when={elsewhereCount() > 0}>
        <div class="dim elsewhere">+{elsewhereCount()} elsewhere</div>
      </Show>
      <div class="band-stats">
        <span>Cohesion {Math.round(store.gameState?.band.belief_cohesion ?? 0)}</span>
        <span>Food {Math.round(store.gameState?.band.shared_food ?? 0)}</span>
      </div>
    </div>
  );
}
