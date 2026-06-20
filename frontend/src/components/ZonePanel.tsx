import { For, Show } from "solid-js";
import { store } from "../store/gameStore";
import type { Zone } from "../types";

export default function ZonePanel() {
  const currentZone = (): Zone | undefined => {
    const player = store.gameState?.characters.find((c) => c.is_player);
    return store.gameState?.world_zones.find((z) => z.id === player?.current_zone_id);
  };

  const connectedZones = (): Zone[] => {
    const zone = currentZone();
    if (!zone) return [];
    return zone.connected_zone_ids
      .map((id) => store.gameState?.world_zones.find((z) => z.id === id))
      .filter((z): z is Zone => z !== undefined);
  };

  const dangerBars = (level: number) => {
    const filled = Math.round(level * 5);
    return "█".repeat(filled) + "░".repeat(5 - filled);
  };

  return (
    <div class="panel zone-panel">
      <div class="panel-title">ZONE</div>
      <Show when={currentZone()} fallback={<div class="dim">—</div>}>
        {(zone) => (
          <>
            <div class="zone-name">{zone().name}</div>
            <div class="zone-desc dim">{zone().description}</div>
            <div class="danger-row">
              <span class="dim">Danger </span>
              <span
                style={{
                  color: zone().danger_level > 0.5 ? "var(--red)" : "var(--green)",
                  "font-family": "monospace",
                }}
              >
                {dangerBars(zone().danger_level)}
              </span>
            </div>
            <div class="connections-title dim">Paths:</div>
            <For each={connectedZones()}>
              {(z) => <div class="connection-item">→ {z.name}</div>}
            </For>
          </>
        )}
      </Show>
    </div>
  );
}
