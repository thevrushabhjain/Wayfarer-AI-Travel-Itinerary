"use client";

import { CalendarDays, MapPin, Users, Wallet } from "lucide-react";
import Image from "next/image";

import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { TripOverview } from "@/lib/types";

const DESTINATION_IMAGE =
  "https://images.unsplash.com/photo-1700646751436-4605e23147db?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NjZ8MHwxfHNlYXJjaHw0fHx0b2t5byUyMGNpdHklMjBzdHJlZXR8ZW58MHx8fGJsYWNrX2FuZF93aGl0ZXwxNzgyOTg3MDczfDA&ixlib=rb-4.1.0&q=85";

function parseDate(value: string): Date | undefined {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? undefined : d;
}

export function TripOverviewCard({ overview }: { overview: TripOverview }) {
  const start = parseDate(overview.start_date);
  const end = parseDate(overview.end_date);
  const hasCalendarDates = Boolean(start && end);

  const stats = [
    { icon: MapPin, label: "Destination", value: overview.destination },
    {
      icon: CalendarDays,
      label: "Duration",
      value: `${overview.duration_days} day${overview.duration_days === 1 ? "" : "s"}`,
    },
    { icon: Users, label: "Travelers", value: `${overview.travelers}` },
    {
      icon: Wallet,
      label: "Budget",
      value: `${overview.total_budget.toLocaleString()} ${overview.currency}`,
    },
  ];

  return (
    <div data-testid="trip-overview-card" className="relative overflow-hidden rounded-xl border border-zinc-800">
      <div className="absolute inset-0">
        <Image
          src={DESTINATION_IMAGE}
          alt={overview.destination}
          fill
          priority
          sizes="(max-width: 1024px) 100vw, 1024px"
          className="object-cover opacity-60 grayscale"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-black/30" />
      </div>

      <div className="relative z-10 flex flex-col gap-6 p-6 sm:p-10">
        <div className="space-y-3">
          <p className="font-mono text-xs uppercase tracking-widest text-zinc-400">Trip Overview</p>
          <h1 data-testid="trip-destination" className="text-3xl font-medium tracking-tight text-white sm:text-5xl">
            {overview.destination}
          </h1>
          <p className="max-w-2xl text-sm text-zinc-300 sm:text-base">{overview.trip_summary}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {stats.map(({ icon: Icon, label, value }) => (
            <div key={label} className="rounded-lg border border-white/10 bg-black/40 p-4">
              <Icon className="mb-2 h-4 w-4 text-zinc-400" strokeWidth={1.5} />
              <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">{label}</p>
              <p className="mt-1 text-sm font-medium text-zinc-100 sm:text-base">{value}</p>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Popover>
            <PopoverTrigger asChild>
              <button
                type="button"
                data-testid="trip-dates-trigger"
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-xs text-zinc-300 transition-colors hover:border-white/30"
              >
                <CalendarDays className="h-3.5 w-3.5" strokeWidth={1.5} />
                {hasCalendarDates ? `${overview.start_date} → ${overview.end_date}` : "Exact dates flexible"}
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-auto border-zinc-800 bg-zinc-950 p-2">
              <Calendar
                mode="range"
                selected={hasCalendarDates ? { from: start, to: end } : undefined}
                defaultMonth={start}
                numberOfMonths={1}
                disabled
                className="text-zinc-100"
              />
            </PopoverContent>
          </Popover>
          <span className="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-xs text-zinc-300">
            {overview.best_time_note}
          </span>
        </div>
      </div>
    </div>
  );
}
