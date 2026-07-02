"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

import type { ProgressStage } from "@/lib/types";
import { cn } from "@/lib/utils";

const STAGES: { key: NonNullable<ProgressStage>; label: string }[] = [
  { key: "understanding", label: "Understanding your request" },
  { key: "planning", label: "Planning itinerary" },
  { key: "finalizing", label: "Finalizing itinerary" },
];

export function ProgressIndicator({ stage }: { stage: ProgressStage }) {
  if (!stage) return null;
  const activeIndex = STAGES.findIndex((s) => s.key === stage);

  return (
    <motion.div
      data-testid="progress-indicator"
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 4 }}
      transition={{ duration: 0.2 }}
      className="flex items-center gap-3 sm:gap-5 py-2"
    >
      {STAGES.map((s, i) => {
        const isDone = i < activeIndex;
        const isActive = i === activeIndex;
        return (
          <div key={s.key} className="flex items-center gap-2">
            <span
              className={cn(
                "flex h-4 w-4 items-center justify-center rounded-full border text-[10px] transition-colors",
                isDone && "border-white bg-white text-black",
                isActive && "border-white",
                !isDone && !isActive && "border-zinc-700"
              )}
            >
              {isDone ? (
                <Check className="h-2.5 w-2.5" strokeWidth={2} />
              ) : (
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    isActive ? "bg-white animate-blink" : "bg-zinc-700"
                  )}
                />
              )}
            </span>
            <span
              className={cn(
                "font-mono text-xs uppercase tracking-widest transition-colors",
                isActive ? "text-zinc-100" : isDone ? "text-zinc-500" : "text-zinc-600"
              )}
            >
              {s.label}
            </span>
          </div>
        );
      })}
    </motion.div>
  );
}
