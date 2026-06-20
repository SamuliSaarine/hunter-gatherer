const API_BASE = `${window.location.protocol}//${window.location.host}/api`;

export async function createNewGame(
  playerName: string,
  difficulty: string = "normal"
): Promise<any> {
  const res = await fetch(`${API_BASE}/game/new`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_name: playerName, difficulty }),
  });
  if (!res.ok) throw new Error("Failed to create game");
  return res.json();
}

export async function getGameState(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/game/state/${sessionId}`);
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export async function listSaves(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/game/saves`);
  if (!res.ok) return [];
  return res.json();
}

export async function loadGame(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/game/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Failed to load game");
  return res.json();
}

export async function getLegacy(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/legacy`);
  if (!res.ok) return [];
  return res.json();
}
