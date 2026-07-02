"use client";

import { Star } from "lucide-react";
import Image from "next/image";

import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { Hotel } from "@/lib/types";

const HOTEL_IMAGE =
  "https://images.unsplash.com/photo-1558976825-6b1b03a03719?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBob3RlbCUyMHJvb218ZW58MHx8fGJsYWNrX2FuZF93aGl0ZXwxNzgyOTg3MDczfDA&ixlib=rb-4.1.0&q=85";

export function HotelsSection({ hotels }: { hotels: Hotel[] }) {
  return (
    <section data-testid="hotels-section">
      <SectionHeader overline="Where to Stay" title="Hotels" testId="hotels-header" />
      <div className="grid gap-4 sm:grid-cols-2">
        {hotels.map((hotel) => (
          <div
            key={hotel.name}
            data-testid={`hotel-card-${hotel.name.replace(/\s+/g, "-").toLowerCase()}`}
            className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950/60"
          >
            <div className="relative h-32 w-full">
              <Image src={HOTEL_IMAGE} alt={hotel.name} fill sizes="(max-width: 768px) 100vw, 400px" className="object-cover grayscale" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              <Badge className="absolute right-3 top-3 border-white/20 bg-black/60 text-zinc-100" variant="outline">
                {hotel.tier}
              </Badge>
            </div>
            <div className="space-y-2 p-5">
              <div className="flex items-baseline justify-between gap-2">
                <h3 className="text-base font-medium text-zinc-100">{hotel.name}</h3>
                <span className="flex items-center gap-1 font-mono text-xs text-zinc-400">
                  <Star className="h-3 w-3 fill-zinc-400 text-zinc-400" strokeWidth={1} />
                  {hotel.rating}
                </span>
              </div>
              <p className="text-xs text-zinc-500">{hotel.area}</p>
              <p className="text-sm text-zinc-400">{hotel.why_recommended}</p>
              <p className="font-mono text-xs text-zinc-300">{hotel.price_range}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
