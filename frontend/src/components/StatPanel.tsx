import { Show } from "solid-js";
import { store } from "../store/gameStore";
import type { Character, GameState } from "../types";

function StatBar(props: { label: string; value: number }) {
  const pct = () => Math.round(Math.max(0, Math.min(100, props.value)));
  const color = () =>
    props.value > 60 ? "var(--green)" : props.value > 30 ? "var(--yellow)" : "var(--red)";

  return (
    <div class="stat-row">
      <span class="stat-label">{props.label}</span>
      <div class="stat-bar-track">
        <div
          class="stat-bar-fill"
          style={{ width: `${pct()}%`, "background-color": color() }}
        />
      </div>
      <span class="stat-value">{pct()}</span>
    </div>
  );
}

export default function StatPanel() {
  const player = (): Character | undefined =>
    store.gameState?.characters.find((c) => c.is_player);
  const state = (): GameState | null => store.gameState;

  return (
    <div class="panel stat-panel">
      <div class="panel-title">VITALS</div>
      <Show when={player()} fallback={<div class="dim">—</div>}>
        {(p) => (
          <>
            <StatBar label="Health" value={p().health} />
            <StatBar label="Hunger" value={p().hunger} />
            <StatBar label="Stamina" value={Math.max(0, 100 - p().fatigue)} />
            <StatBar label="Rep" value={p().reputation} />
            <div class="stat-divider" />
            <div class="season-info">
              {state()?.current_season?.toUpperCase()} · Day {state()?.current_day} ·
              Yr {state()?.current_year}
            </div>
            <div class="difficulty-badge">{state()?.difficulty?.toUpperCase()}</div>
          </>
        )}
      </Show>
    </div>
  );
}
