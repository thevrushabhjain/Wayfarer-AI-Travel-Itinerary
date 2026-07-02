"use client";

import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { FoodExperience } from "@/lib/types";

export function FoodExperiencesSection({ items }: { items: FoodExperience[] }) {
  return (
    <section data-testid="food-experiences-section">
      <SectionHeader overline="Taste the Place" title="Food & Local Experiences" testId="food-experiences-header" />
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((item, idx) => (
          <div
            key={idx}
            data-testid={`food-experience-${idx}`}
            className="space-y-2 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4"
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-sm font-medium text-zinc-100">{item.name}</h4>
              {item.must_try && (
                <Badge className="border-white/20 bg-white text-black" variant="outline">
                  Must try
                </Badge>
              )}
            </div>
            <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">{item.type}</p>
            <p className="text-sm text-zinc-400">{item.description}</p>
            <p className="font-mono text-xs text-zinc-500">{item.price_range}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
