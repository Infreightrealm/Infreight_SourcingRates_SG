"use client";

import { useState } from "react";
import { ArrowRight, Check, Download, Loader2, Minus, Table2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { BatchRouteResult } from "@/lib/excelExport";
import { cn } from "@/lib/utils";

type Phase = "waiting" | "quotes" | "empty" | "failed";
type Filter = "all" | "quotes" | "waiting" | "empty";

function lanePhase(item: BatchRouteResult): Phase {
  if (item.status === "failed") return "failed";
  if (item.status !== "completed") return "waiting";
  const quotes = item.searchResult?.results.reduce((n, r) => n + (r.quotes?.length ?? 0), 0) ?? 0;
  return quotes > 0 ? "quotes" : "empty";
}

/** Cheapest priced quote across the lane's carriers, e.g. "USD 1,010". */
function cheapest(item: BatchRouteResult): string | null {
  let best: { v: number; c: string } | null = null;
  for (const r of item.searchResult?.results ?? []) {
    for (const q of r.quotes ?? []) {
      if (q.final_freight_value > 0 && (!best || q.final_freight_value < best.v)) best = { v: q.final_freight_value, c: q.currency };
    }
  }
  return best ? `${best.c} ${best.v.toLocaleString("en-US", { maximumFractionDigits: 0 })}` : null;
}

const PHASE_STYLE: Record<Phase, string> = {
  waiting: "bg-primary/10 text-primary",
  quotes: "bg-success/12 text-success-foreground",
  empty: "bg-muted text-muted-foreground",
  failed: "bg-destructive/10 text-destructive-foreground",
};

interface BatchProgressPanelProps {
  items: BatchRouteResult[];
  isRunning: boolean;
  /** Destination of the lane whose results are on screen, to highlight it. */
  viewingDestination?: string;
  onView: (index: number) => void;
  onExportAll: () => void;
  onExportTariff: () => void;
}

/**
 * v2 batch panel for RFQ batches: progress and counts, the two Excel exports, and
 * a filterable lane list with each lane's status and cheapest quote; clicking a
 * finished lane shows its results below. Classic keeps its own panel.
 */
export default function BatchProgressPanel({ items, isRunning, viewingDestination, onView, onExportAll, onExportTariff }: BatchProgressPanelProps) {
  const [filter, setFilter] = useState<Filter>("all");

  const phases = items.map(lanePhase);
  const count = (p: Phase) => phases.filter((x) => x === p).length;
  const done = items.length - count("waiting");
  const pct = items.length ? Math.round((done / items.length) * 100) : 0;
  const finished = !isRunning || done === items.length;
  const totalQuotes = items.reduce((n, it) => n + (it.searchResult?.results.reduce((m, r) => m + (r.quotes?.length ?? 0), 0) ?? 0), 0);

  const filters: Array<[Filter, string, number]> = [
    ["all", "All", items.length],
    ["quotes", "With quotes", count("quotes")],
    ["waiting", "Still searching", count("waiting")],
    ["empty", "No quotes", count("empty") + count("failed")],
  ];
  const shown = items
    .map((item, i) => ({ item, i, phase: phases[i]! }))
    .filter(({ phase }) =>
      filter === "all" ? true : filter === "empty" ? phase === "empty" || phase === "failed" : phase === filter,
    );

  return (
    <Card className="flex flex-col gap-4 p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-foreground" aria-live="polite">
            {finished ? "Batch search finished" : "Batch search running"} · {done} of {items.length} lanes done
          </h2>
          <p className="text-xs text-muted-foreground">
            {count("quotes")} with quotes · {count("empty")} no quotes · {count("failed")} failed
            {!finished && ` · ${count("waiting")} still searching`} · {totalQuotes} quote{totalQuotes === 1 ? "" : "s"} in total
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={onExportTariff} title="Rate matrix in the EX PASIR GUDANG 1st / 2nd half 20' and 40' layout">
            <Table2 className="size-4" />
            Tariff sheet (PG / TPP)
          </Button>
          <Button onClick={onExportAll} disabled={totalQuotes === 0 && finished}>
            <Download className="size-4" />
            Export all lanes
          </Button>
        </div>
      </div>

      <div
        className="h-2 overflow-hidden rounded-full bg-secondary"
        role="progressbar"
        aria-label="Lanes finished"
        aria-valuemin={0}
        aria-valuemax={items.length}
        aria-valuenow={done}
      >
        <div className={cn("h-full rounded-full transition-[width] duration-500", finished ? "bg-success" : "bg-primary")} style={{ width: `${pct}%` }} />
      </div>

      <div role="radiogroup" aria-label="Show lanes" className="flex flex-wrap gap-1">
        {filters.map(([id, label, n]) => (
          <button
            key={id}
            type="button"
            role="radio"
            aria-checked={filter === id}
            onClick={() => setFilter(id)}
            className={cn(
              "min-h-9 rounded-lg px-3 text-sm font-medium transition-colors",
              filter === id ? "bg-primary/10 font-semibold text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {label} <span className="opacity-70">{n}</span>
          </button>
        ))}
      </div>

      <ol className="grid max-h-80 grid-cols-1 gap-1.5 overflow-y-auto pr-1 sm:grid-cols-2 xl:grid-cols-3">
        {shown.map(({ item, i, phase }) => {
          const price = phase === "quotes" ? cheapest(item) : null;
          const viewing = !!item.searchResult && viewingDestination === item.destination;
          const status =
            phase === "waiting" ? "Searching…" : phase === "failed" ? "Failed" : phase === "empty" ? "No quotes" : price ? `from ${price}` : "Quotes found";
          return (
            <li key={`${item.origin}-${item.destination}-${i}`}>
              <button
                type="button"
                onClick={() => onView(i)}
                aria-current={viewing ? "true" : undefined}
                className={cn(
                  "flex min-h-12 w-full items-center gap-2.5 rounded-lg border px-3 py-1.5 text-left transition-colors",
                  viewing ? "border-primary bg-primary/8" : "border-border bg-background hover:bg-accent",
                )}
              >
                <span className="w-7 shrink-0 text-xs font-semibold text-muted-foreground">{i + 1}</span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-1 truncate text-sm font-semibold text-foreground">
                    <span className="truncate">{item.destination}</span>
                  </span>
                  <span className="flex items-center gap-1 truncate text-[11px] text-muted-foreground">
                    from {item.origin}
                    {viewing && (
                      <>
                        <ArrowRight className="size-3" aria-hidden /> showing below
                      </>
                    )}
                  </span>
                </span>
                <span className={cn("inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold", PHASE_STYLE[phase])}>
                  {phase === "waiting" && <Loader2 className="size-3 animate-spin" aria-hidden />}
                  {phase === "quotes" && <Check className="size-3" strokeWidth={3} aria-hidden />}
                  {phase === "empty" && <Minus className="size-3" aria-hidden />}
                  {phase === "failed" && <X className="size-3" strokeWidth={3} aria-hidden />}
                  {status}
                </span>
              </button>
            </li>
          );
        })}
        {shown.length === 0 && <li className="col-span-full py-6 text-center text-sm text-muted-foreground">No lanes here.</li>}
      </ol>
      <p className="text-xs text-muted-foreground">Click a lane to see its quotes below.</p>
    </Card>
  );
}
