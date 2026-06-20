const API_BASE = `${window.location.protocol}//${window.location.host}/api`;
const AUTH_BASE = `${window.location.protocol}//${window.location.host}/auth`;

export async function checkAuth(): Promise<boolean> {
  const res = await fetch(`${AUTH_BASE}/check`, { credentials: "include" });
  if (!res.ok) return false;
  const data = await res.json();
  return data.authenticated;
}

export async function login(password: string): Promise<void> {
  const res = await fetch(`${AUTH_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? "Wrong password");
  }
}

export async function logout(): Promise<void> {
  await fetch(`${AUTH_BASE}/logout`, { method: "POST", credentials: "include" });
}

export async function createNewGame(
  playerName: string,
  difficulty: string = "normal"
): Promise<any> {
  const res = await fetch(`${API_BASE}/game/new`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_name: playerName, difficulty }),
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to create game");
  return res.json();
}

export async function getGameState(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/game/state/${sessionId}`, { credentials: "include" });
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export async function listSaves(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/game/saves`, { credentials: "include" });
  if (!res.ok) return [];
  return res.json();
}

export async function loadGame(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/game/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Failed to load game");
  return res.json();
}

export async function getLegacy(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/legacy`, { credentials: "include" });
  if (!res.ok) return [];
  return res.json();
}
