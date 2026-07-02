"use client";

import { AnimatePresence } from "framer-motion";

import { ChatInput } from "@/components/chat/ChatInput";
import { ProgressIndicator } from "@/components/chat/ProgressIndicator";
import type { ProgressStage } from "@/lib/types";

interface RefineBarProps {
  onSend: (text: string) => void;
  isSending: boolean;
  progressStage: ProgressStage;
}

export function RefineBar({ onSend, isSending, progressStage }: RefineBarProps) {
  return (
    <div data-testid="refine-bar" className="sticky bottom-0 z-30 border-t border-zinc-900 bg-black/90 backdrop-blur">
      <div className="mx-auto max-w-5xl px-6 py-4">
        <AnimatePresence>{progressStage && <ProgressIndicator stage={progressStage} />}</AnimatePresence>
        <ChatInput
          onSend={onSend}
          isSending={isSending}
          placeholder="Refine your itinerary — e.g. 'make day 2 more relaxed' or 'swap a hotel for something cheaper'"
        />
      </div>
    </div>
  );
}
