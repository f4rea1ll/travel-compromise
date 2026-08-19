const API_BASE = "http://localhost:8000";

export async function createSession() {
  const res = await fetch(`${API_BASE}/session/create`, { method: "POST" });
  if (!res.ok) throw new Error("Не удалось создать сессию");
  return res.json();
}

export async function submitParticipant(sessionId, participantNumber, data) {
  const res = await fetch(
    `${API_BASE}/session/${sessionId}/join/${participantNumber}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error("Не удалось отправить анкету");
  return res.json();
}

export async function getSessionStatus(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/status`);
  if (!res.ok) throw new Error("Сессия не найдена");
  return res.json();
}

export async function getResult(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/result`);
  if (!res.ok) throw new Error("Не удалось получить результат");
  return res.json();
}