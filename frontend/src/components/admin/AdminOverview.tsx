"use client";

import { useState, type ReactNode } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, CircleSlash, MapPin, RefreshCw, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AdminSection } from "./AdminSidebar";

export type AnalyticsRange = "all" | "30d" | "14d" | "7d" | "today";

interface CarrierStat {
  carrier: string;
  carrier_name: string;
  total_queries: number;
  quotes_found_count: number;
  accuracy_percent: number;
  failure_count: number;
  failure_percent: number;
  connector_not_available_percent?: number;
  port_mismatch_count: number;
}

interface LaneStat {
  display_lane: string;
  search_count: number;
  hit_rate_percent: number;
  min_price: number | null;
  cheapest_carrier: string | null;
}

interface UserStat {
  user_name: string;
  search_count: number;
  last_active: string | null;
}

export interface AdminAnalytics {
  summary?: {
    total_searches?: number;
    total_quotes?: number;
    hit_rate_percent?: number;
    searches_with_quotes?: number;
    distinct_lanes?: number;
    active_users_count?: number;
    most_active_lane?: { display_lane?: string } | null;
  };
  timeline?: { busiest_day?: number; per_day?: Array<{ iso: string; label: string; searches: number; quotes: number }> };
  top_lanes?: LaneStat[];
  carrier_ranking?: CarrierStat[];
  user_leaderboard?: UserStat[];
  all_users?: string[];
}

export interface AdminOverviewUser {
  id: string;
  status: "active" | "pending" | "disabled";
  display_name?: string;
  name?: string;
  username?: string;
}

interface AdminOverviewProps {
  data: AdminAnalytics | null;
  loading: boolean;
  users: AdminOverviewUser[];
  range: AnalyticsRange;
  onRangeChange: (range: AnalyticsRange) => void;
  userFilter: string;
  onUserFilterChange: (user: string) => void;
  onRefresh: () => void;
  onNavigate: (section: AdminSection) => void;
}

const RANGES: Array<[AnalyticsRange, string]> = [
  ["today", "Today"],
  ["7d", "7 days"],
  ["30d", "30 days"],
  ["all", "All time"],
];

/** Fewer searches than this and a carrier's percentages aren't worth acting on. */
const MIN_SEARCHES = 5;
/** Share of a carrier's searches ending in an error or time-out that counts as failing. */
const FAILING_PERCENT = 25;

type Tone = "good" | "warn" | "bad" | "neutral";

const TONE_PILL: Record<Tone, string> = {
  good: "bg-success/12 text-success-foreground",
  warn: "bg-warning/15 text-warning-foreground",
  bad: "bg-destructive/10 text-destructive-foreground",
  neutral: "bg-muted text-muted-foreground",
};

function carrierState(c: CarrierStat): { label: string; tone: Tone } {
  if ((c.connector_not_available_percent ?? 0) >= 80) return { label: "Not connected", tone: "neutral" };
  if (c.total_queries < MIN_SEARCHES) return { label: "Few searches", tone: "neutral" };
  if (c.failure_percent >= FAILING_PERCENT) return { label: "Failing", tone: "bad" };
  if (c.port_mismatch_count > 0) return { label: "Port mismatches", tone: "warn" };
  if (c.accuracy_percent >= 60) return { label: "Healthy", tone: "good" };
  return { label: "Mostly no quotes", tone: "warn" };
}

/** Backend timestamps are UTC but may lack a zone suffix. */
function relativeTime(iso: string | null | undefined): string {
  if (!iso) return "never";
  const t = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`).getTime();
  if (Number.isNaN(t)) return "unknown";
  const mins = Math.round((Date.now() - t) / 60000);
  if (mins < 2) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.round(hours / 24);
  return days === 1 ? "yesterday" : `${days} days ago`;
}

function initials(name: string) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]!.toUpperCase())
      .join("") || "?"
  );
}

const userName = (u: AdminOverviewUser) => u.display_name || u.name || u.username || "Unnamed";
const num = (n: number | undefined) => (n ?? 0).toLocaleString("en-US");

interface Attention {
  key: string;
  tone: Exclude<Tone, "good">;
  icon: ReactNode;
  title: string;
  detail: string;
  action: string;
  section: AdminSection;
}

function attentionItems(data: AdminAnalytics | null, users: AdminOverviewUser[]): Attention[] {
  const items: Attention[] = [];
  const pending = users.filter((u) => u.status === "pending");
  if (pending.length) {
    items.push({
      key: "pending",
      tone: "warn",
      icon: <UserPlus className="size-[18px]" aria-hidden />,
      title: pending.length === 1 ? "1 person is waiting for access" : `${pending.length} people are waiting for access`,
      detail: `${pending.map(userName).join(", ")}. They can't search until approved.`,
      action: "Review requests",
      section: "users",
    });
  }
  const carriers = data?.carrier_ranking ?? [];
  for (const c of carriers) {
    if (c.total_queries >= MIN_SEARCHES && c.failure_percent >= FAILING_PERCENT) {
      items.push({
        key: `failing-${c.carrier}`,
        tone: "bad",
        icon: <AlertTriangle className="size-[18px]" aria-hidden />,
        title: `${c.carrier_name} failed ${c.failure_count} of its ${c.total_queries} searches`,
        detail: "Failed means an error or time-out, not just no quotes. See which routes it fails on.",
        action: "Route reliability",
        section: "route_health",
      });
    }
  }
  const mismatched = carriers.filter((c) => c.port_mismatch_count > 0);
  if (mismatched.length) {
    const total = mismatched.reduce((n, c) => n + c.port_mismatch_count, 0);
    items.push({
      key: "ports",
      tone: "warn",
      icon: <MapPin className="size-[18px]" aria-hidden />,
      title: `${total} search${total === 1 ? "" : "es"} where a carrier picked a different port than asked`,
      detail: `${mismatched.map((c) => `${c.carrier_name} (${c.port_mismatch_count})`).join(", ")}. A port name fix tells the bot the name that carrier uses.`,
      action: "Port name fixes",
      section: "overrides",
    });
  }
  return items;
}

/**
 * v2 admin landing page: what needs an admin's attention, headline numbers, carrier
 * health, searches per day, busiest lanes and team activity, all from the analytics
 * and users data the classic admin tabs already load.
 */
export default function AdminOverview({
  data,
  loading,
  users,
  range,
  onRangeChange,
  userFilter,
  onUserFilterChange,
  onRefresh,
  onNavigate,
}: AdminOverviewProps) {
  const [hoveredDay, setHoveredDay] = useState<number | null>(null);
  const s = data?.summary ?? {};
  const attention = attentionItems(data, users);
  const days = data?.timeline?.per_day ?? [];
  const busiest = Math.max(1, data?.timeline?.busiest_day ?? 1);
  const peakIndex = days.reduce((best, d, i) => (d.searches > (days[best]?.searches ?? -1) ? i : best), 0);
  const lanes = (data?.top_lanes ?? []).slice(0, 5);
  const team = (data?.user_leaderboard ?? []).slice(0, 5);
  const carriers = data?.carrier_ranking ?? [];
  const perSearch = s.total_searches ? (s.total_quotes ?? 0) / s.total_searches : 0;

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Overview</h1>
          <p className="text-sm text-muted-foreground">What needs you today, and how sourcing is going.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div role="radiogroup" aria-label="Time range" className="flex gap-0.5 rounded-lg border border-border bg-card p-0.5">
            {RANGES.map(([id, label]) => (
              <button
                key={id}
                type="button"
                role="radio"
                aria-checked={range === id}
                onClick={() => onRangeChange(id)}
                className={cn(
                  "min-h-9 rounded-md px-3 text-sm transition-colors",
                  range === id ? "bg-primary/10 font-semibold text-primary" : "font-medium text-muted-foreground hover:text-foreground",
                )}
              >
                {label}
              </button>
            ))}
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            Team member
            <select
              value={userFilter}
              onChange={(e) => onUserFilterChange(e.target.value)}
              className="min-h-10 rounded-lg border border-border bg-card px-2.5 text-sm text-foreground"
            >
              <option value="all">Everyone</option>
              {(data?.all_users ?? []).map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </label>
          <Button variant="outline" size="icon" onClick={onRefresh} disabled={loading} aria-label="Refresh">
            <RefreshCw className={cn("size-4", loading && "animate-spin")} />
          </Button>
        </div>
      </div>

      <Card className="overflow-hidden p-0">
        <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3.5">
          <h2 className="text-base font-bold text-foreground">
            Needs attention <span className="font-medium text-muted-foreground">· {attention.length}</span>
          </h2>
        </div>
        {attention.length === 0 ? (
          <p className="flex items-center gap-2 px-5 py-4 text-sm text-muted-foreground">
            <CheckCircle2 className="size-4 text-success" aria-hidden />
            {loading && !data ? "Checking…" : "Nothing needs you right now."}
          </p>
        ) : (
          <ul>
            {attention.map((item) => (
              <li key={item.key} className="flex flex-wrap items-center gap-x-4 gap-y-3 border-b border-border/60 px-5 py-3.5 last:border-b-0">
                <span className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg", TONE_PILL[item.tone])}>{item.icon}</span>
                <div className="min-w-0 flex-[1_1_320px]">
                  <p className="font-semibold text-foreground">{item.title}</p>
                  <p className="text-sm text-muted-foreground">{item.detail}</p>
                </div>
                <Button variant={item.key === "pending" ? "default" : "outline"} onClick={() => onNavigate(item.section)}>
                  {item.action}
                  <ArrowRight className="size-4" />
                </Button>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <section aria-label="Headline numbers" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          ["Searches run", num(s.total_searches), `by ${num(s.active_users_count)} ${s.active_users_count === 1 ? "person" : "people"}`],
          ["Quotes returned", num(s.total_quotes), `${perSearch.toFixed(1)} per search`],
          ["Searches with a quote", `${s.hit_rate_percent ?? 0}%`, `${num(s.searches_with_quotes)} of ${num(s.total_searches)}`],
          ["Lanes searched", num(s.distinct_lanes), s.most_active_lane?.display_lane ? `busiest: ${s.most_active_lane.display_lane}` : "no searches yet"],
        ].map(([label, value, sub]) => (
          <Card key={label} className="px-4 py-3.5">
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="mt-0.5 text-[28px] font-bold leading-tight text-foreground">{value}</p>
            <p className="truncate text-xs text-muted-foreground" title={sub}>
              {sub}
            </p>
          </Card>
        ))}
      </section>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.15fr_1fr]">
        <Card className="overflow-hidden p-0">
          <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3.5">
            <h2 className="text-base font-bold text-foreground">Carrier health</h2>
            <Button variant="link" size="sm" onClick={() => onNavigate("analytics")}>
              Details
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[480px] text-sm">
              <thead>
                <tr className="text-left text-xs text-muted-foreground">
                  <th scope="col" className="px-5 py-2.5 font-semibold">Carrier</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Searches</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Got quotes</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Failed</th>
                  <th scope="col" className="px-5 py-2.5 font-semibold">State</th>
                </tr>
              </thead>
              <tbody>
                {carriers.map((c) => {
                  const state = carrierState(c);
                  return (
                    <tr key={c.carrier} className="border-t border-border/60">
                      <td className="px-5 py-2.5 font-semibold text-foreground">{c.carrier_name}</td>
                      <td className="px-2 py-2.5 text-right">{num(c.total_queries)}</td>
                      <td className="px-2 py-2.5 text-right">{c.accuracy_percent}%</td>
                      <td className="px-2 py-2.5 text-right">{num(c.failure_count)}</td>
                      <td className="px-5 py-2.5">
                        <span className={cn("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold", TONE_PILL[state.tone])}>
                          {state.tone === "good" && <CheckCircle2 className="size-3" aria-hidden />}
                          {(state.tone === "warn" || state.tone === "bad") && <AlertTriangle className="size-3" aria-hidden />}
                          {state.tone === "neutral" && <CircleSlash className="size-3" aria-hidden />}
                          {state.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
                {carriers.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-5 py-6 text-center text-muted-foreground">
                      {loading ? "Loading…" : "No carrier searches in this period."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="flex flex-col gap-3 px-5 py-3.5">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className="text-base font-bold text-foreground">Searches per day</h2>
            <span className="text-sm text-muted-foreground" aria-live="polite">
              {hoveredDay !== null && days[hoveredDay]
                ? `${days[hoveredDay].label}: ${days[hoveredDay].searches} searches, ${days[hoveredDay].quotes} quotes`
                : days.length
                  ? `peak ${days[peakIndex]?.searches ?? 0} on ${days[peakIndex]?.label}`
                  : ""}
            </span>
          </div>
          <div className="flex h-40 items-end gap-0.5 border-b border-border" onMouseLeave={() => setHoveredDay(null)} aria-hidden>
            {days.map((d, i) => (
              <div key={d.iso} className="flex h-full flex-1 items-end justify-center" onMouseEnter={() => setHoveredDay(i)}>
                <div
                  className={cn(
                    "w-full max-w-[22px] rounded-t-[4px] transition-colors",
                    d.searches === 0 ? "bg-border" : hoveredDay === i ? "bg-primary" : "bg-primary/65",
                  )}
                  style={{ height: d.searches ? `${Math.max(4, (d.searches / busiest) * 100)}%` : "2px" }}
                />
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-muted-foreground" aria-hidden>
            <span>{days[0]?.label}</span>
            <span>{days[days.length - 1]?.label}</span>
          </div>
          <table className="sr-only">
            <caption>Searches and quotes per day</caption>
            <thead>
              <tr>
                <th scope="col">Day</th>
                <th scope="col">Searches</th>
                <th scope="col">Quotes</th>
              </tr>
            </thead>
            <tbody>
              {days.map((d) => (
                <tr key={d.iso}>
                  <td>{d.label}</td>
                  <td>{d.searches}</td>
                  <td>{d.quotes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[2fr_1fr]">
        <Card className="overflow-hidden p-0">
          <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3.5">
            <h2 className="text-base font-bold text-foreground">Busiest lanes</h2>
            <Button variant="link" size="sm" onClick={() => onNavigate("analytics")}>
              All {num(data?.top_lanes?.length)} lanes
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-sm">
              <thead>
                <tr className="text-left text-xs text-muted-foreground">
                  <th scope="col" className="px-5 py-2.5 font-semibold">Lane</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Searches</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">With quotes</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Lowest quote</th>
                  <th scope="col" className="px-5 py-2.5 font-semibold">From</th>
                </tr>
              </thead>
              <tbody>
                {lanes.map((l) => (
                  <tr key={l.display_lane} className="border-t border-border/60">
                    <td className="px-5 py-2.5 font-semibold text-foreground">{l.display_lane}</td>
                    <td className="px-2 py-2.5 text-right">{num(l.search_count)}</td>
                    <td className="px-2 py-2.5 text-right">{l.hit_rate_percent}%</td>
                    <td className="px-2 py-2.5 text-right">{l.min_price ? `USD ${num(Math.round(l.min_price))}` : "–"}</td>
                    <td className="px-5 py-2.5">{l.min_price ? l.cheapest_carrier ?? "–" : "–"}</td>
                  </tr>
                ))}
                {lanes.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-5 py-6 text-center text-muted-foreground">
                      {loading ? "Loading…" : "No searches in this period."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="overflow-hidden p-0">
          <div className="border-b border-border px-5 py-3.5">
            <h2 className="text-base font-bold text-foreground">Team activity</h2>
          </div>
          <ul className="py-1">
            {team.map((u) => (
              <li key={u.user_name} className="flex items-center gap-2.5 px-5 py-2.5">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-foreground text-[11px] font-bold text-background" aria-hidden>
                  {initials(u.user_name)}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold text-foreground">{u.user_name}</p>
                  <p className="text-xs text-muted-foreground">active {relativeTime(u.last_active)}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-foreground">{num(u.search_count)}</p>
                  <p className="text-xs text-muted-foreground">searches</p>
                </div>
              </li>
            ))}
            {team.length === 0 && <li className="px-5 py-6 text-center text-sm text-muted-foreground">{loading ? "Loading…" : "No activity in this period."}</li>}
          </ul>
        </Card>
      </div>
    </div>
  );
}
