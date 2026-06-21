import { Match, Switch } from "solid-js";
import { store, setStore, addNarrativeEntry } from "./store/gameStore";
import LoginScreen from "./components/LoginScreen";
import StartScreen from "./components/StartScreen";
import NarrativeScroll from "./components/NarrativeScroll";
import PlayerInput from "./components/PlayerInput";
import StatPanel from "./components/StatPanel";
import ZonePanel from "./components/ZonePanel";
import BandPanel from "./components/BandPanel";
import MobileStats from "./components/MobileStats";

function GameLayout() {
  return (
    <div class="game-layout">
      <header class="game-header">
        <span class="header-title">HUNTER-GATHERER</span>
        <span class="header-band">{store.gameState?.band.name ?? ""}</span>
        <MobileStats />
        <span class={`conn-dot ${store.isConnected ? "connected" : "disconnected"}`}>●</span>
      </header>

      <div class="game-body">
        <div class="left-panel">
          <NarrativeScroll />
          <PlayerInput />
        </div>
        <div class="right-panel">
          <StatPanel />
          <ZonePanel />
          <BandPanel />
          <MythPanel />
        </div>
      </div>
    </div>
  );
}

function DeathScreen() {
  const lastGmEntry = () =>
    [...store.narrative].reverse().find((e) => e.type === "gm")?.text ?? "";

  return (
    <div class="death-screen">
      <div class="death-title">YOU HAVE FALLEN</div>
      <div class="death-cause">{store.deathCause}</div>
      <div class="death-narrative dim">{lastGmEntry()}</div>
      <button
        class="start-btn"
        onClick={() => {
          setStore("screen", "start");
          setStore("gameState", null);
          setStore("narrative", []);
          setStore("isDead", false);
          setStore("deathCause", null);
          setStore("streamingText", "");
        }}
      >
        Return to Camp
      </button>
    </div>
  );
}

export default function App() {
  return (
    <Switch>
      <Match when={store.screen === "login"}>
        <LoginScreen />
      </Match>
      <Match when={store.screen === "start"}>
        <StartScreen />
      </Match>
      <Match when={store.screen === "game"}>
        <GameLayout />
      </Match>
      <Match when={store.screen === "death"}>
        <DeathScreen />
      </Match>
    </Switch>
  );
}
