"use client";

import { ArrowUp } from "lucide-react";
import { useState, type KeyboardEvent } from "react";

import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (text: string) => void;
  isSending: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export function ChatInput({ onSend, isSending, placeholder, autoFocus }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    if (!value.trim() || isSending) return;
    onSend(value);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      data-testid="chat-input-container"
      className="flex items-end gap-2 rounded-xl border border-zinc-800 bg-zinc-950/80 p-2 pl-4 backdrop-blur transition-colors focus-within:border-zinc-600"
    >
      <textarea
        data-testid="chat-input"
        value={value}
        autoFocus={autoFocus}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder ?? "Tell me about your trip..."}
        rows={1}
        disabled={isSending}
        className="max-h-32 flex-1 resize-none bg-transparent py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none disabled:opacity-50"
      />
      <button
        type="button"
        data-testid="chat-send-button"
        onClick={handleSubmit}
        disabled={isSending || !value.trim()}
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors",
          value.trim() && !isSending
            ? "bg-white text-black hover:bg-zinc-200"
            : "bg-zinc-800 text-zinc-500"
        )}
      >
        <ArrowUp className="h-4 w-4" strokeWidth={1.5} />
      </button>
    </div>
  );
}
