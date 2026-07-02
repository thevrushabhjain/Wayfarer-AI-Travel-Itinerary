"use client";

import { Bus, Car, Footprints, Plane, Ship, TrainFront } from "lucide-react";

import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { TransportOption } from "@/lib/types";

const MODE_ICON: Record<string, typeof Plane> = {
  flight: Plane,
  train: TrainFront,
  metro: TrainFront,
  bus: Bus,
  taxi: Car,
  rideshare: Car,
  "rental car": Car,
  ferry: Ship,
  walking: Footprints,
};

export function TransportationSection({ options, currency }: { options: TransportOption[]; currency: string }) {
  return (
    <section data-testid="transportation-section">
      <SectionHeader overline="Getting Around" title="Transportation" testId="transportation-header" />
      <div className="grid gap-3 sm:grid-cols-2">
        {options.map((option, idx) => {
          const Icon = MODE_ICON[option.mode] ?? Car;
          return (
            <div
              key={idx}
              data-testid={`transport-option-${idx}`}
              className="flex gap-3 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-zinc-800 bg-black">
                <Icon className="h-4 w-4 text-zinc-400" strokeWidth={1.5} />
              </span>
              <div className="space-y-1">
                <div className="flex items-baseline justify-between gap-2">
                  <h4 className="text-sm font-medium capitalize text-zinc-100">{option.mode}</h4>
                  <span className="font-mono text-xs text-zinc-500">
                    {option.estimated_cost ? `${currency} ${option.estimated_cost}` : "Free"}
                  </span>
                </div>
                <p className="text-sm text-zinc-400">{option.description}</p>
                <p className="text-xs text-zinc-500">{option.tips}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
