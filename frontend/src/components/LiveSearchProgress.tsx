"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Check, Loader2, Minus, MonitorPlay, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CARRIERS, STATUS_MAP, containerLabel } from "@/lib/types";
import type { CarrierResultSchema, RateSearchResultResponse } from "@/lib/types";
import { openLiveViewer } from "@/lib/liveViewer";
import { cn } from "@/lib/utils";

type Phase = "queued" | "running" | "action" | "quotes" | "empty" | "failed";

/** Statuses where a person has to step in through the live browser. */
const ACTION_STATUSES = new Set([
  "WAITING_FOR_HUMAN_VERIFICATION",
  "CAPTCHA_OR_MANUAL_REVIEW_REQUIRED",
  "MANUAL_ACTION_REQUIRED",
  "BOT_CHALLENGE_DETECTED",
]);

const EMPTY_STATUSES = new Set(["NO_QUOTES_AVAILABLE", "CONNECTOR_NOT_AVAILABLE"]);

const TERMINAL_SEARCH = new Set(["COMPLETED", "PARTIAL_COMPLETED", "FAILED"]);

const PHASE_STYLE: Record<Phase, string> = {
  queued: "bg-muted text-muted-foreground",
  running: "bg-primary/10 text-primary",
  action: "bg-warning/15 text-warning-foreground",
  quotes: "bg-success/12 text-success-foreground",
  empty: "bg-muted text-muted-foreground",
  failed: "bg-destructive/10 text-destructive-foreground",
};

interface ChipModel {
  carrier: string;
  name: string;
  color: string;
  phase: Phase;
  label: string;
  detail?: string;
}

function describe(r: CarrierResultSchema): ChipModel {
  const meta = CARRIERS.find((c) => c.code === r.carrier);
  const base = { carrier: r.carrier, name: meta?.name ?? r.carrier, color: meta?.color ?? "currentColor", detail: r.error_message };
  const status = r.status || "QUEUED";
  const quotes = r.quotes?.length ?? 0;

  if (status === "QUEUED") return { ...base, phase: "queued", label: "Queued" };
  if (status.startsWith("RUNNING")) {
    const size = containerLabel(status.substring(7).trim().replace(/[()]/g, ""));
    const sofar = quotes > 0 ? ` · ${quotes} so far` : "";
    return { ...base, phase: "running", label: (size ? `Searching ${size}…` : "Searching…") + sofar };
  }
  if (ACTION_STATUSES.has(status)) return { ...base, phase: "action", label: STATUS_MAP[status]?.label ?? "Action required" };
  if (quotes > 0) return { ...base, phase: "quotes", label: `${quotes} quote${quotes === 1 ? "" : "s"}` };
  if (EMPTY_STATUSES.has(status)) {
    return { ...base, phase: "empty", label: status === "NO_QUOTES_AVAILABLE" ? "No quotes on this lane" : "Not available" };
  }
  return { ...base, phase: "failed", label: STATUS_MAP[status]?.label ?? status };
}

function PhaseIcon({ phase }: { phase: Phase }) {
  const cls = "size-3.5 shrink-0";
  if (phase === "running") return <Loader2 className={cn(cls, "animate-spin")} aria-hidden />;
  if (phase === "quotes") return <Check className={cls} strokeWidth={3} aria-hidden />;
  if (phase === "action") return <AlertTriangle className={cls} aria-hidden />;
  if (phase === "failed") return <X className={cls} strokeWidth={3} aria-hidden />;
  return <Minus className={cls} aria-hidden />;
}

function formatElapsed(ms: number) {
  const s = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(s / 60);
  return m > 0 ? `${m} min ${s % 60} s` : `${s} s`;
}

interface LiveSearchProgressProps {
  result: RateSearchResultResponse | null;
  isLoading: boolean;
  /** Whether the floating live viewer is switched on in Workspace › Panels. */
  liveViewerEnabled: boolean;
  onEnableLiveViewer: () => void;
}

/**
 * One chip per carrier that updates on every poll: queued, searching, quotes
 * found, no quotes, failed, or waiting for a person (with a button that opens
 * the live browser on that carrier).
 */
export default function LiveSearchProgress({ result, isLoading, liveViewerEnabled, onEnableLiveViewer }: LiveSearchProgressProps) {
  const chips = (result?.results ?? []).map(describe);
  const total = chips.length;
  const settled = chips.filter((c) => c.phase !== "queued" && c.phase !== "running" && c.phase !== "action").length;
  const withQuotes = chips.filter((c) => c.phase === "quotes").length;
  const quoteCount = (result?.results ?? []).reduce((n, r) => n + (r.quotes?.length ?? 0), 0);
  // Batch routes can be viewed while they still run, so "finished" comes from
  // the search itself, not from whether this page is polling.
  const finished = result
    ? TERMINAL_SEARCH.has(result.status) || (total > 0 && settled === total)
    : !isLoading;
  const waiting = chips.filter((c) => c.phase === "action");

  // Elapsed time in this browser. The page remounts this component per search
  // (key = search id), so the clock starts with each search; it stops ticking
  // once the search has finished.
  const [startedAt] = useState(() => Date.now());
  const [now, setNow] = useState(startedAt);
  useEffect(() => {
    if (finished) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [finished]);
  const elapsed = formatElapsed(now - startedAt);

  const title = total === 0
    ? "Starting search…"
    : finished
      ? `Search finished · ${withQuotes} of ${total} carriers returned quotes`
      : `Searching · ${settled} of ${total} carriers done`;
  const pct = total === 0 ? 0 : Math.round((settled / total) * 100);

  const openViewer = (carrier: string) => {
    if (!liveViewerEnabled) onEnableLiveViewer();
    openLiveViewer(carrier);
  };

  return (
    <Card className="animate-fade-in-up flex flex-col gap-3 p-4 sm:px-5">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <h2 className="text-sm font-semibold text-foreground" aria-live="polite">
          {title}
        </h2>
        <div
          className="h-1.5 min-w-40 flex-1 overflow-hidden rounded-full bg-secondary"
          role="progressbar"
          aria-label="Carriers finished"
          aria-valuemin={0}
          aria-valuemax={total || 1}
          aria-valuenow={settled}
        >
          <div
            className={cn(
              "h-full rounded-full transition-[width] duration-500",
              finished ? "bg-success" : "bg-primary",
              total === 0 && "w-1/4 animate-pulse",
            )}
            style={total === 0 ? undefined : { width: `${pct}%` }}
          />
        </div>
        <span className="text-xs text-muted-foreground">
          {elapsed}
          {quoteCount > 0 && ` · ${quoteCount} quote${quoteCount === 1 ? "" : "s"}${finished ? "" : " so far"}`}
          {!finished && " · results appear as each carrier finishes"}
        </span>
      </div>

      {total > 0 && (
        <ul className="flex flex-wrap gap-2" aria-label="Carrier progress">
          {chips.map((c) => (
            <li
              key={c.carrier}
              title={c.detail || undefined}
              className={cn("flex min-h-9 items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm", PHASE_STYLE[c.phase])}
            >
              <span className="size-2 shrink-0 rounded-full ring-1 ring-foreground/15" style={{ backgroundColor: c.color }} aria-hidden />
              <span className="font-semibold text-foreground">{c.name}</span>
              <span className="inline-flex items-center gap-1 text-xs font-semibold">
                <PhaseIcon phase={c.phase} />
                {c.label}
              </span>
              {c.phase === "action" && (
                <Button size="sm" className="ml-1 h-7 bg-warning-foreground text-background hover:bg-warning-foreground/90" onClick={() => openViewer(c.carrier)}>
                  <MonitorPlay className="size-3.5" />
                  Open live viewer
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}

      {waiting.length > 0 && (
        <p className="text-xs text-warning-foreground">
          {waiting.map((c) => c.name).join(" and ")} {waiting.length === 1 ? "is" : "are"} waiting for you in the live
          browser. The search carries on once {waiting.length === 1 ? "it is" : "they are"} solved.
        </p>
      )}
    </Card>
  );
}
