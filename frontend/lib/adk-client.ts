const ADK_BASE = process.env.NEXT_PUBLIC_ADK_URL || "http://localhost:8000";
const APP_NAME = "signal_agent";
const USER_ID = "default_user";

let sessionId: string | null = null;

export async function getOrCreateSession(): Promise<string> {
  if (sessionId) return sessionId;

  const res = await fetch(`${ADK_BASE}/apps/${APP_NAME}/users/${USER_ID}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await res.json();
  sessionId = data.id;
  return sessionId!;
}

export async function sendMessage(message: string): Promise<string> {
  const sid = await getOrCreateSession();
  const res = await fetch(
    `${ADK_BASE}/apps/${APP_NAME}/users/${USER_ID}/sessions/${sid}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: { role: "user", parts: [{ text: message }] },
      }),
    }
  );
  const data = await res.json();
  // Extract text from the last agent message
  const agentMessages = data.filter((e: any) => e.role === "model");
  if (agentMessages.length > 0) {
    const lastMsg = agentMessages[agentMessages.length - 1];
    return lastMsg.parts?.map((p: any) => p.text).join("") || "";
  }
  return JSON.stringify(data);
}

export function streamMessage(
  message: string,
  onChunk: (chunk: string) => void,
  onDone: () => void
): () => void {
  let cancelled = false;

  (async () => {
    const sid = await getOrCreateSession();
    const res = await fetch(
      `${ADK_BASE}/apps/${APP_NAME}/users/${USER_ID}/sessions/${sid}/sse`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: { role: "user", parts: [{ text: message }] },
        }),
      }
    );

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      onDone();
      return;
    }

    while (!cancelled) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      onChunk(text);
    }
    onDone();
  })();

  return () => { cancelled = true; };
}
