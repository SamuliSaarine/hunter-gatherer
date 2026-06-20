import { createSignal, onMount } from "solid-js";
import { checkAuth, login } from "../api/client";
import { setStore } from "../store/gameStore";

export default function LoginScreen() {
  const [password, setPassword] = createSignal("");
  const [error, setError] = createSignal("");
  const [loading, setLoading] = createSignal(true);

  onMount(async () => {
    if (await checkAuth()) {
      setStore("screen", "start");
    }
    setLoading(false);
  });

  const submit = async () => {
    setError("");
    setLoading(true);
    try {
      await login(password());
      setStore("screen", "start");
    } catch (e: any) {
      setError(e.message ?? "Wrong password.");
      setPassword("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="start-screen">
      <div class="start-title">HUNTER-GATHERER</div>
      <div class="start-subtitle dim">Enter password to continue</div>
      <div class="start-form">
        <input
          class="start-input"
          type="password"
          placeholder="Password"
          value={password()}
          onInput={(e) => setPassword(e.currentTarget.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          autofocus
          disabled={loading()}
        />
        <button class="start-btn" onClick={submit} disabled={loading()}>
          {loading() ? "..." : "Enter"}
        </button>
        {error() && <div class="error-msg">{error()}</div>}
      </div>
    </div>
  );
}
