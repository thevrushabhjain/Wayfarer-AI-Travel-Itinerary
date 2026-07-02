"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { fetchHistory, streamChat } from "@/lib/api";
import { getSessionId, setSessionId as persistSessionId } from "@/lib/session";
import type { ChatMessage, ProgressStage, TravelItinerary, TripInfo } from "@/lib/types";

export function useChat() {
  const [sessionId, setSessionIdState] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [tripInfo, setTripInfo] = useState<TripInfo | null>(null);
  const [itinerary, setItinerary] = useState<TravelItinerary | null>(null);
  const [progressStage, setProgressStage] = useState<ProgressStage>(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  const idCounter = useRef(0);
  const nextId = () => `msg-${Date.now()}-${idCounter.current++}`;

  useEffect(() => {
    const existing = getSessionId();
    if (!existing) {
      setInitialized(true);
      return;
    }
    setSessionIdState(existing);
    fetchHistory(existing)
      .then((history) => {
        if (!history) {
          setInitialized(true);
          return;
        }
        setTripInfo(history.trip_info);
        setMessages(
          history.messages.map((m) => ({
            id: nextId(),
            role: m.role,
            content: m.content,
            createdAt: new Date(m.created_at).getTime(),
          }))
        );
        if (history.itinerary) setItinerary(history.itinerary);
        setInitialized(true);
      })
      .catch(() => setInitialized(true));
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isSending) return;

      setError(null);
      setMessages((prev) => [...prev, { id: nextId(), role: "user", content: trimmed, createdAt: Date.now() }]);
      setIsSending(true);
      setProgressStage("understanding");

      await streamChat(trimmed, sessionId, {
        onProgress: (stage) => setProgressStage(stage),
        onResult: (result) => {
          if (result.session_id && result.session_id !== sessionId) {
            setSessionIdState(result.session_id);
            persistSessionId(result.session_id);
          }
          if (result.trip_info) setTripInfo(result.trip_info);
          if (result.type === "itinerary" && result.itinerary) {
            setItinerary(result.itinerary);
          }
          setMessages((prev) => [
            ...prev,
            { id: nextId(), role: "assistant", content: result.reply, createdAt: Date.now() },
          ]);
        },
        onError: (detail) => {
          setError(detail);
        },
      });

      setIsSending(false);
      setProgressStage(null);
    },
    [sessionId, isSending]
  );

  return {
    sessionId,
    messages,
    tripInfo,
    itinerary,
    progressStage,
    isSending,
    error,
    initialized,
    sendMessage,
  };
}
