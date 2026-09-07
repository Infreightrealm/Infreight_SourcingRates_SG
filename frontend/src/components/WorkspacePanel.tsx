"use client";

import { useEffect } from "react";
import { useTheme } from "next-themes";
import {
  Anchor,
  Bot,
  Check,
  Gauge,
  LayoutGrid,
  Mail,
  Monitor,
  MonitorPlay,
  Moon,
  Pin,
  PlayCircle,
  RotateCcw,
  Sun,
  Trash2,
  X,
} from "lucide-react";
import { toast } from "sonner";

import UsageStats from "./UsageStats";
import { ACCENTS, laneLabel, usePreferences, type SavedLane } from "@/lib/preferences";
import { cn } from "@/lib/utils";

interface WorkspacePanelProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string | null;
  /** The route currently in the search form, offered as a pinnable lane. */
  currentLane?: { origin: string; destination: string; containerTypes: string[]; weightKg: number };
  onSelectLane: (lane: SavedLane) => void;
  onReplayIntro: () => void;
}

function Section({
  icon,
  title,
  hint,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2.5">
        <span className="inline-flex size-7 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-primary [&_svg]:size-3.5">
          {icon}
        </span>
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-foreground">{title}</h3>
          {hint && <p className="text-[11px] text-muted-foreground">{hint}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}

/** Selectable card — the shared shape for theme, accent and panel choices. */
function ChoiceCard({
  selected,
  onClick,
  children,
  className,
  ...rest
}: React.ComponentProps<"button"> & { selected: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        "btn-interactive relative flex flex-col items-start gap-2 rounded-xl border p-3 text-left",
        selected
          ? "border-primary/45 bg-primary/8 shadow-panel"
          : "border-border bg-card hover:bg-accent",
        className,
      )}
      {...rest}
    >
      {selected && (
        <span className="absolute right-2 top-2 inline-flex size-4 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Check className="size-2.5" strokeWidth={3} />
        </span>
      )}
      {children}
    </button>
  );
}

function Toggle({ on }: { on: boolean }) {
  return (
    <span
      className={cn(
        "relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors",
        on ? "bg-primary" : "bg-muted-foreground/30",
      )}
    >
      <span
        className={cn(
          "size-3.5 rounded-full bg-white shadow-sm transition-transform duration-200 ease-[cubic-bezier(0.16,1,0.3,1)]",
          on ? "translate-x-[1.15rem]" : "translate-x-[0.185rem]",
        )}
      />
    </span>
  );
}

export default function WorkspacePanel({
  isOpen,
  onClose,
  userName,
  currentLane,
  onSelectLane,
  onReplayIntro,
}: WorkspacePanelProps) {
  const { prefs, setPreferences, setPanel, addLane, removeLane, resetPreferences } =
    usePreferences();
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const canPin =
    !!currentLane?.origin?.trim() &&
    !!currentLane?.destination?.trim() &&
    !prefs.lanes.some(
      (l) =>
        l.origin === currentLane.origin &&
        l.destination === currentLane.destination &&
        l.containerTypes.join("+") === currentLane.containerTypes.join("+"),
    );

  const panelToggles: Array<{
    key: keyof typeof prefs.panels;
    icon: React.ReactNode;
    label: string;
    hint: string;
  }> = [
    { key: "rfq", icon: <Mail />, label: "Quote from an email", hint: "AI RFQ reader panel" },
    { key: "liveViewer", icon: <MonitorPlay />, label: "Live browser viewer", hint: "Watch carrier portals; needed for CAPTCHAs" },
    { key: "assistant", icon: <Bot />, label: "AI assistant", hint: "Floating chat launcher" },
  ];

  return (
    <>
      <div
        className="animate-blur-in fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-sm"
        onClick={onClose}
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-label="Workspace preferences"
        className="animate-slide-in-spring fixed right-0 top-0 z-50 flex h-full w-full max-w-xl flex-col border-l border-border bg-popover text-popover-foreground shadow-card-hover"
      >
        <header className="flex items-start justify-between gap-3 border-b border-border px-6 py-5">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-foreground">Your workspace</h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {userName ? `Saved in this browser for ${userName}.` : "Saved in this browser."} Nothing
              here changes your search results.
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close workspace"
            className="btn-interactive shrink-0 rounded-lg border border-border bg-secondary p-2 text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </header>

        <div className="flex-1 space-y-8 overflow-y-auto px-6 py-6">
          {/* ── Activity ───────────────────────────────── */}
          <Section
            icon={<Gauge />}
            title="Your activity"
            hint={userName ? `Rate searches recorded for ${userName}` : "Rate searches recorded"}
          >
            <UsageStats key={userName ?? "all"} userName={userName} />
          </Section>

          {/* ── Saved lanes ────────────────────────────── */}
          <Section
            icon={<Pin />}
            title="Saved lanes"
            hint="Pin a route to load it straight into the search form"
          >
            {canPin && currentLane && (
              <button
                type="button"
                onClick={() => {
                  const ok = addLane({
                    origin: currentLane.origin,
                    destination: currentLane.destination,
                    containerTypes: currentLane.containerTypes,
                    weightKg: currentLane.weightKg,
                  });
                  toast[ok ? "success" : "info"](
                    ok ? "Lane pinned to your workspace" : "That lane is already pinned",
                  );
                }}
                className="btn-interactive flex w-full items-center gap-2 rounded-xl border border-dashed border-primary/40 bg-primary/6 px-3.5 py-3 text-left text-xs font-medium text-primary hover:bg-primary/12"
              >
                <Pin className="size-3.5" />
                Pin current route — {laneLabel(currentLane.origin)} →{" "}
                {laneLabel(currentLane.destination)}
              </button>
            )}

            {prefs.lanes.length === 0 ? (
              <p className="rounded-xl border border-dashed border-border px-4 py-6 text-center text-xs text-muted-foreground">
                No pinned lanes yet. Fill in an origin and destination, then pin it from here.
              </p>
            ) : (
              <div className="grid gap-2 sm:grid-cols-2">
                {prefs.lanes.map((lane) => (
                  <div
                    key={lane.id}
                    className="card-hover group relative rounded-xl border border-border bg-card p-3"
                  >
                    <button
                      type="button"
                      onClick={() => {
                        onSelectLane(lane);
                        onClose();
                        toast.success(
                          `Loaded ${laneLabel(lane.origin)} → ${laneLabel(lane.destination)}`,
                        );
                      }}
                      className="block w-full text-left"
                    >
                      <div className="flex items-center gap-1.5 font-mono text-xs font-semibold text-foreground">
                        <Anchor className="size-3 shrink-0 text-primary" />
                        <span className="truncate">{laneLabel(lane.origin)}</span>
                        <span className="text-muted-foreground">→</span>
                        <span className="truncate">{laneLabel(lane.destination)}</span>
                      </div>
                      <p className="mt-1 truncate text-[11px] text-muted-foreground">
                        {lane.origin.split(",")[0]} to {lane.destination.split(",")[0]}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {lane.containerTypes.map((ct) => (
                          <span
                            key={ct}
                            className="rounded border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground"
                          >
                            {ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct}
                          </span>
                        ))}
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => removeLane(lane.id)}
                      aria-label={`Remove ${laneLabel(lane.origin)} to ${laneLabel(lane.destination)}`}
                      className="absolute right-1.5 top-1.5 rounded-md p-1.5 text-muted-foreground opacity-0 transition-opacity hover:bg-accent hover:text-destructive-foreground focus-visible:opacity-100 group-hover:opacity-100"
                    >
                      <Trash2 className="size-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </Section>

          {/* ── Appearance ─────────────────────────────── */}
          <Section icon={<Sun />} title="Appearance" hint="Applies across the whole console">
            <div className="space-y-3">
              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Theme
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {(
                    [
                      { id: "light", label: "Light", icon: <Sun /> },
                      { id: "dark", label: "Dark", icon: <Moon /> },
                      { id: "system", label: "System", icon: <Monitor /> },
                    ] as const
                  ).map((opt) => (
                    <ChoiceCard
                      key={opt.id}
                      selected={theme === opt.id}
                      onClick={() => setTheme(opt.id)}
                    >
                      <span className="text-muted-foreground [&_svg]:size-4">{opt.icon}</span>
                      <span className="text-xs font-medium text-foreground">{opt.label}</span>
                    </ChoiceCard>
                  ))}
                </div>
              </div>

              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Accent
                </p>
                <div className="flex flex-wrap gap-2">
                  {ACCENTS.map((a) => {
                    const selected = prefs.accent === a.id;
                    return (
                      <button
                        key={a.id}
                        type="button"
                        aria-pressed={selected}
                        aria-label={`${a.label} accent`}
                        onClick={() => setPreferences({ accent: a.id })}
                        className={cn(
                          "btn-interactive flex items-center gap-2 rounded-lg border py-1.5 pl-2 pr-3 text-xs font-medium",
                          selected
                            ? "border-primary/45 bg-primary/8 text-foreground"
                            : "border-border bg-card text-muted-foreground hover:bg-accent hover:text-foreground",
                        )}
                      >
                        <span
                          className="inline-flex size-4 items-center justify-center rounded-full"
                          style={{ background: a.swatch }}
                        >
                          {selected && <Check className="size-2.5 text-white" strokeWidth={3.5} />}
                        </span>
                        {a.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Rates grid density
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {(
                    [
                      { id: "comfortable", label: "Comfortable", hint: "Roomier rows" },
                      { id: "compact", label: "Compact", hint: "More sailings per screen" },
                    ] as const
                  ).map((opt) => (
                    <ChoiceCard
                      key={opt.id}
                      selected={prefs.density === opt.id}
                      onClick={() => setPreferences({ density: opt.id })}
                    >
                      <span className="text-xs font-medium text-foreground">{opt.label}</span>
                      <span className="text-[11px] text-muted-foreground">{opt.hint}</span>
                    </ChoiceCard>
                  ))}
                </div>
              </div>
            </div>
          </Section>

          {/* ── Panels ─────────────────────────────────── */}
          <Section
            icon={<LayoutGrid />}
            title="Panels"
            hint="Hide what you don't use — this browser only"
          >
            <div className="space-y-2">
              {panelToggles.map((p) => {
                const on = prefs.panels[p.key];
                return (
                  <button
                    key={p.key}
                    type="button"
                    role="switch"
                    aria-checked={on}
                    onClick={() => setPanel(p.key, !on)}
                    className="btn-interactive flex w-full items-center gap-3 rounded-xl border border-border bg-card p-3 text-left hover:bg-accent"
                  >
                    <span className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-muted-foreground [&_svg]:size-4">
                      {p.icon}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-xs font-medium text-foreground">{p.label}</span>
                      <span className="block truncate text-[11px] text-muted-foreground">
                        {p.hint}
                      </span>
                    </span>
                    <Toggle on={on} />
                  </button>
                );
              })}
            </div>
          </Section>
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-border bg-muted/40 px-6 py-4">
          <button
            type="button"
            onClick={() => {
              onClose();
              onReplayIntro();
            }}
            className="btn-interactive inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            <PlayCircle className="size-3.5" />
            Replay intro
          </button>
          <button
            type="button"
            onClick={() => {
              resetPreferences();
              setTheme("system");
              toast.info("Workspace reset to defaults");
            }}
            className="btn-interactive inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            <RotateCcw className="size-3.5" />
            Reset to defaults
          </button>
        </footer>
      </div>
    </>
  );
}
