"use client";

import { Compass, RotateCcw } from "lucide-react";

interface DashboardHeaderProps {
  onReset: () => void;
}

export function DashboardHeader({ onReset }: DashboardHeaderProps) {
  return (
    <header data-testid="dashboard-header" className="sticky top-0 z-30 border-b border-zinc-900 bg-black/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <Compass className="h-4 w-4 text-zinc-300" strokeWidth={1.5} />
          <span className="text-sm font-medium tracking-tight text-zinc-100">Wayfarer</span>
        </div>
        <button
          type="button"
          data-testid="new-trip-button"
          onClick={onReset}
          className="flex items-center gap-1.5 rounded-md border border-zinc-800 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:border-zinc-600 hover:text-zinc-200"
        >
          <RotateCcw className="h-3 w-3" strokeWidth={1.5} />
          Plan another trip
        </button>
      </div>
    </header>
  );
}
