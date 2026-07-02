"use client";

import { useMemo, useState } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { PackingItem } from "@/lib/types";

export function PackingChecklistSection({ items }: { items: PackingItem[] }) {
  const [filter, setFilter] = useState<string>("all");
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const categories = useMemo(() => {
    const unique = Array.from(new Set(items.map((i) => i.category)));
    return ["all", ...unique];
  }, [items]);

  const filtered = filter === "all" ? items : items.filter((i) => i.category === filter);

  return (
    <section data-testid="packing-checklist-section">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <SectionHeader overline="Don't Forget" title="Packing Checklist" testId="packing-checklist-header" />
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger data-testid="packing-filter-select" className="w-40 border-zinc-800 bg-transparent text-zinc-200">
            <SelectValue placeholder="Filter" />
          </SelectTrigger>
          <SelectContent className="border-zinc-800 bg-zinc-950 text-zinc-200">
            {categories.map((c) => (
              <SelectItem key={c} value={c} className="capitalize">
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {filtered.map((item) => {
          const isChecked = Boolean(checked[item.item]);
          return (
            <label
              key={item.item}
              data-testid={`packing-item-${item.item.replace(/\s+/g, "-").toLowerCase()}`}
              className="flex cursor-pointer items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-950/60 px-4 py-3 transition-colors hover:border-zinc-700"
            >
              <Checkbox
                checked={isChecked}
                onCheckedChange={(value) => setChecked((prev) => ({ ...prev, [item.item]: Boolean(value) }))}
                className="border-zinc-600 data-[state=checked]:bg-white data-[state=checked]:text-black"
              />
              <span className={`flex-1 text-sm ${isChecked ? "text-zinc-500 line-through" : "text-zinc-200"}`}>
                {item.item}
              </span>
              {item.essential && !isChecked && (
                <span className="font-mono text-[10px] uppercase tracking-widest text-zinc-500">essential</span>
              )}
            </label>
          );
        })}
      </div>
    </section>
  );
}
