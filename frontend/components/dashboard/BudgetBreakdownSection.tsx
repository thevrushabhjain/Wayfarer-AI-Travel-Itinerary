"use client";

import { SectionHeader } from "@/components/dashboard/SectionHeader";
import type { BudgetBreakdown } from "@/lib/types";

export function BudgetBreakdownSection({ budget }: { budget: BudgetBreakdown }) {
  return (
    <section data-testid="budget-breakdown-section">
      <SectionHeader overline="Spending Plan" title="Budget Breakdown" testId="budget-breakdown-header" />

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
          <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">Total Budget</p>
          <p data-testid="budget-total" className="mt-1 font-mono text-xl text-zinc-50">
            {budget.currency} {budget.total_budget.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
          <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">Daily Average</p>
          <p className="mt-1 font-mono text-xl text-zinc-50">
            {budget.currency} {budget.daily_average.toLocaleString()}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {budget.items.map((item) => (
          <div key={item.category} data-testid={`budget-item-${item.category.toLowerCase()}`} className="space-y-1.5">
            <div className="flex items-baseline justify-between">
              <span className="text-sm font-medium text-zinc-200">{item.category}</span>
              <span className="font-mono text-sm text-zinc-400">
                {budget.currency} {item.amount.toLocaleString()} · {item.percentage.toFixed(0)}%
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-900">
              <div
                className="h-full rounded-full bg-zinc-200"
                style={{ width: `${Math.min(item.percentage, 100)}%` }}
              />
            </div>
            <p className="text-xs text-zinc-500">{item.notes}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
