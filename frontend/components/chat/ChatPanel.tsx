"use client";

import { motion } from "framer-motion";
import { Compass } from "lucide-react";
import { useEffect, useRef } from "react";

import { ChatInput } from "@/components/chat/ChatInput";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ProgressIndicator } from "@/components/chat/ProgressIndicator";
import type { ChatMessage, ProgressStage } from "@/lib/types";

const SUGGESTIONS = [
  "5 days in Tokyo for 2 people, we love food and quirky neighborhoods",
  "A relaxed week in Lisbon on a $2000 budget",
  "Weekend trip to New York, first time visiting",
];

interface ChatPanelProps {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  isSending: boolean;
  progressStage: ProgressStage;
}

export function ChatPanel({ messages, onSend, isSending, progressStage }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const hasMessages = messages.length > 0;

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, progressStage]);

  return (
    <div data-testid="chat-panel" className="relative z-10 mx-auto flex min-h-screen w-full max-w-2xl flex-col px-6">
      {!hasMessages ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-8 pb-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center gap-5"
          >
            <span className="flex h-11 w-11 items-center justify-center rounded-full border border-zinc-800">
              <Compass className="h-5 w-5 text-zinc-200" strokeWidth={1.5} />
            </span>
            <div className="space-y-2">
              <h1 className="text-4xl font-medium tracking-tight text-zinc-50 sm:text-5xl">Wayfarer</h1>
              <p className="text-sm text-zinc-400 sm:text-base">
                Describe your trip in plain language. I&apos;ll ask what&apos;s missing, then build the full itinerary.
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="w-full space-y-3"
          >
            <ChatInput onSend={onSend} isSending={isSending} autoFocus />
            <div data-testid="chat-suggestions" className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  data-testid="chat-suggestion-chip"
                  onClick={() => onSend(s)}
                  className="rounded-full border border-zinc-800 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:border-zinc-600 hover:text-zinc-200"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      ) : (
        <div className="flex flex-1 flex-col pt-16">
          <div ref={scrollRef} data-testid="chat-message-list" className="flex-1 space-y-5 overflow-y-auto pb-40 pt-4 no-scrollbar">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            <ProgressIndicator stage={progressStage} />
          </div>
          <div className="fixed inset-x-0 bottom-0 z-20 mx-auto w-full max-w-2xl bg-gradient-to-t from-black via-black/95 to-transparent px-6 pb-6 pt-10">
            <ChatInput onSend={onSend} isSending={isSending} />
          </div>
        </div>
      )}
    </div>
  );
}
