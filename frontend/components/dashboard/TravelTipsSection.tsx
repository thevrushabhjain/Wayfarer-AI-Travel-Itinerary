"use client";

import { AlertTriangle, Banknote, Cloud, Globe, HeartHandshake, MessageCircle, Wifi } from "lucide-react";

import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { TravelTip } from "@/lib/types";

const CATEGORY_ICON: Record<string, typeof Globe> = {
  culture: Globe,
  safety: AlertTriangle,
  money: Banknote,
  language: MessageCircle,
  weather: Cloud,
  connectivity: Wifi,
  etiquette: HeartHandshake,
};

export function TravelTipsSection({ tips }: { tips: TravelTip[] }) {
  return (
    <section data-testid="travel-tips-section">
      <SectionHeader overline="Good to Know" title="Travel Tips" testId="travel-tips-header" />
      <div className="grid gap-3 sm:grid-cols-2">
        {tips.map((tip, idx) => {
          const Icon = CATEGORY_ICON[tip.category] ?? Globe;
          return (
            <div
              key={idx}
              data-testid={`travel-tip-${idx}`}
              className="flex gap-3 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-zinc-800 bg-black">
                <Icon className="h-4 w-4 text-zinc-400" strokeWidth={1.5} />
              </span>
              <div className="space-y-0.5">
                <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">{tip.category}</p>
                <p className="text-sm text-zinc-300">{tip.tip}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
