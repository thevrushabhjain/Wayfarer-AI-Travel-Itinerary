"use client";

import { motion } from "framer-motion";

import type { ChatMessage } from "@/lib/types";
import { cn } from "@/lib/utils";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      data-testid={`chat-message-${message.role}`}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[75%] whitespace-pre-wrap text-sm leading-relaxed",
          isUser
            ? "rounded-lg bg-zinc-900 px-4 py-3 text-zinc-100"
            : "rounded-lg py-1 text-zinc-300"
        )}
      >
        {message.content}
      </div>
    </motion.div>
  );
}
