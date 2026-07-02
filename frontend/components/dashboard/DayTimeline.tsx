"use client";

import {
  Bus,
  Camera,
  ShoppingBag,
  Sparkles,
  Utensils,
  Mountain,
  Moon,
  MapPin,
  Clock,
} from "lucide-react";

import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { DayPlan } from "@/lib/types";

const CATEGORY_ICON: Record<string, typeof Camera> = {
  sightseeing: Camera,
  food: Utensils,
  culture: Sparkles,
  adventure: Mountain,
  leisure: Moon,
  transport: Bus,
  shopping: ShoppingBag,
  nightlife: Moon,
};

function formatCurrency(value: number, currency = "USD") {
  if (!value) return "Free";
  return `${currency} ${value.toLocaleString()}`;
}

export function DayTimeline({ days, currency }: { days: DayPlan[]; currency: string }) {
  return (
    <section data-testid="day-timeline-section">
      <SectionHeader overline="Day-by-Day" title="Timeline" testId="day-timeline-header" />
      <div className="space-y-10">
        {days.map((day) => (
          <div key={day.day_number} data-testid={`day-plan-${day.day_number}`} className="relative pl-8">
            <div className="absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full border border-zinc-700 bg-black font-mono text-[11px] text-zinc-300">
              {day.day_number}
            </div>
            <div className="absolute bottom-0 left-3 top-8 w-px bg-zinc-800" />

            <div className="mb-4">
              <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">
                DAY {String(day.day_number).padStart(2, "0")} · {day.date}
              </p>
              <h3 className="text-lg font-medium text-zinc-100 sm:text-xl">{day.theme}</h3>
            </div>

            <div className="space-y-4">
              {day.activities.map((activity, idx) => {
                const Icon = CATEGORY_ICON[activity.category] ?? Camera;
                return (
                  <div
                    key={idx}
                    data-testid={`activity-${day.day_number}-${idx}`}
                    className="group rounded-xl border border-zinc-800 bg-zinc-950/60 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900/60"
                  >
                    <div className="flex items-start gap-3">
                      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-zinc-800 bg-black">
                        <Icon className="h-4 w-4 text-zinc-400" strokeWidth={1.5} />
                      </span>
                      <div className="flex-1 space-y-1.5">
                        <div className="flex flex-wrap items-baseline justify-between gap-2">
                          <h4 className="text-sm font-medium text-zinc-100 sm:text-base">{activity.title}</h4>
                          <span className="font-mono text-xs text-zinc-500">{activity.time}</span>
                        </div>
                        <p className="text-sm text-zinc-400">{activity.description}</p>
                        <div className="flex flex-wrap items-center gap-3 pt-1 font-mono text-xs text-zinc-500">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" strokeWidth={1.5} />
                            {activity.location}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" strokeWidth={1.5} />
                            {activity.duration_hours}h
                          </span>
                          <span>{formatCurrency(activity.estimated_cost, currency)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
