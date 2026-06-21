import { Show } from "solid-js";
import { store } from "../store/gameStore";

function MiniBar(props: { value: number; color: string }) {
  const pct = () => Math.max(0, Math.min(100, props.value));
  return (
    <div class="mini-bar-track">
      <div class="mini-bar-fill" style={{ width: `${pct()}%`, background: props.color }} />
    </div>
  );
}

export default function MobileStats() {
  const player = () => store.gameState?.characters.find((c) => c.is_player);
  const state = () => store.gameState;

  return (
    <Show when={player()}>
      {(p) => (
        <div class="mobile-stats">
          <div class="mobile-stat">
            <span class="mobile-stat-label">HP</span>
            <MiniBar value={p().health} color={p().health > 60 ? "var(--green)" : p().health > 30 ? "var(--yellow)" : "var(--red)"} />
          </div>
          <div class="mobile-stat">
            <span class="mobile-stat-label">FOOD</span>
            <MiniBar value={p().hunger} color={p().hunger > 60 ? "var(--green)" : p().hunger > 30 ? "var(--yellow)" : "var(--red)"} />
          </div>
          <div class="mobile-stat">
            <span class="mobile-stat-label">REP</span>
            <MiniBar value={p().reputation} color="var(--amber)" />
          </div>
          <span class="mobile-season">{state()?.current_season?.slice(0, 3).toUpperCase()} Y{state()?.current_year}</span>
        </div>
      )}
    </Show>
  );
}
