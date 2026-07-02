import type { ProgressStage, SessionHistory, StreamResult } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

interface StreamCallbacks {
  onProgress: (stage: ProgressStage) => void;
  onResult: (result: StreamResult) => void;
  onError: (detail: string) => void;
}

function parseSseBlock(block: string): { event: string; data: string } | null {
  const lines = block.split("\n");
  let event = "message";
  let data = "";
  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      data += line.slice(5).trim();
    }
  }
  if (!data) return null;
  return { event, data };
}

export async function streamChat(
  message: string,
  sessionId: string | null,
  callbacks: StreamCallbacks
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
  } catch {
    callbacks.onError("Could not reach the planning service. Please check your connection and try again.");
    return;
  }

  if (!response.ok || !response.body) {
    callbacks.onError("The planning service returned an unexpected error. Please try again.");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";

    for (const block of blocks) {
      if (!block.trim()) continue;
      const parsed = parseSseBlock(block);
      if (!parsed) continue;

      try {
        const payload = JSON.parse(parsed.data);
        if (parsed.event === "progress") {
          callbacks.onProgress(payload.stage as ProgressStage);
        } else if (parsed.event === "result") {
          callbacks.onResult(payload as StreamResult);
        } else if (parsed.event === "error") {
          callbacks.onError(payload.detail as string);
        }
      } catch {
        // Ignore malformed SSE chunks rather than crashing the stream.
      }
    }
  }
}

export async function fetchHistory(sessionId: string): Promise<SessionHistory | null> {
  try {
    const response = await fetch(`${API_URL}/api/chat/${sessionId}/history`);
    if (!response.ok) return null;
    return (await response.json()) as SessionHistory;
  } catch {
    return null;
  }
}
