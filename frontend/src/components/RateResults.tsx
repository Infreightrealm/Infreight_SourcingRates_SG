"use client";

import { useMemo, useState } from "react";
import { Check, ChevronDown, ClipboardCopy, Download, MoveRight, TriangleAlert, X } from "lucide-react";
import { toast } from "sonner";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CARRIERS, containerLabel, type ChargeSchema, type QuoteSchema, type RateSearchResultResponse } from "@/lib/types";
import { formatQuoteDate } from "@/lib/formatQuoteDate";
import { cn } from "@/lib/utils";

type SortKey = "price" | "transit" | "departure";

const SIZE_ORDER = ["DRY 20", "DRY 40", "DRY 40H", "REEFER 20", "REEFER 40"];
const RUNNING = new Set(["QUEUED", "WAITING_FOR_HUMAN_VERIFICATION", "MANUAL_ACTION_REQUIRED"]);

interface Row {
  key: string;
  carrier: string;
  carrierName: string;
  color: string;
  quote: QuoteSchema;
  size: string;
}

function money(amount: number, currency: string) {
  return `${currency} ${amount.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;
}

function dateValue(raw?: string) {
  const t = raw ? Date.parse(raw) : NaN;
  return Number.isNaN(t) ? Number.MAX_SAFE_INTEGER : t;
}

function isSoldOut(q: QuoteSchema) {
  return !q.final_freight_value;
}

function isSpot(q: QuoteSchema) {
  return `${q.vessel ?? ""} ${q.service_name ?? ""}`.toUpperCase().includes("SPOT");
}

function freeTimeText(q: QuoteSchema) {
  const parts: string[] = [];
  if (q.free_time != null) parts.push(/d$|\s/.test(String(q.free_time)) ? String(q.free_time) : `${q.free_time}d free`);
  if (q.demurrage) parts.push(`dem ${q.demurrage}d`);
  if (q.detention) parts.push(`det ${q.detention}d`);
  return parts.join(" · ") || "—";
}

function ChargeList({ charges, empty }: { charges: ChargeSchema[]; empty: string }) {
  if (charges.length === 0) return <p className="text-muted-foreground">{empty}</p>;
  return (
    <ul className="space-y-1">
      {charges.map((c, i) => (
        <li key={`${c.name}-${i}`} className="flex justify-between gap-3">
          <span className="min-w-0">{c.name}</span>
          <span className="shrink-0 tabular-nums">{c.amount ? money(c.amount, c.currency) : "—"}</span>
        </li>
      ))}
    </ul>
  );
}

function Breakdown({ q, onDetails }: { q: QuoteSchema; onDetails: () => void }) {
  return (
    <div className="flex flex-col gap-3 px-4 pb-4 sm:pl-16">
      {(q.warning_message || q.is_breakdown_unavailable) && (
        <p className="flex items-start gap-2 rounded-lg bg-warning/12 px-3 py-2 text-xs text-warning-foreground">
          <TriangleAlert className="mt-0.5 size-3.5 shrink-0" />
          {q.warning_message || "The carrier did not show a charge breakdown for this sailing."}
        </p>
      )}
      <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
        <div className="rounded-lg bg-muted p-3">
          <p className="mb-2 text-xs font-semibold text-muted-foreground">Added to all-in</p>
          <ul className="space-y-1">
            <li className="flex justify-between gap-3">
              <span>Ocean freight</span>
              <span className="tabular-nums">{money(q.basic_ocean_freight, q.currency)}</span>
            </li>
            {q.discount !== 0 && (
              <li className="flex justify-between gap-3">
                <span>Discount</span>
                <span className="tabular-nums">{money(q.discount, q.currency)}</span>
              </li>
            )}
          </ul>
          <div className="mt-1">
            <ChargeList charges={q.included_freight_surcharges} empty="" />
          </div>
          <p className="mt-2 flex justify-between gap-3 border-t border-border pt-2 font-semibold">
            <span>All-in</span>
            <span className="tabular-nums">{money(q.final_freight_value, q.currency)}</span>
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="mb-2 text-xs font-semibold text-muted-foreground">Listed but not added · check these</p>
          <ChargeList charges={q.uncertain_charges} empty="None" />
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="mb-2 text-xs font-semibold text-muted-foreground">Not added · origin / destination</p>
          <ChargeList charges={q.excluded_charges} empty="None" />
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
        <span>
          ETA {formatQuoteDate(q.eta)} · valid till {formatQuoteDate(q.validity_till)} · source {q.source === "carrier_api" ? "carrier API" : "carrier portal"}
        </span>
        <Button size="sm" variant="ghost" onClick={onDetails}>
          Full breakdown
        </Button>
      </div>
    </div>
  );
}

interface RateResultsProps {
  data: RateSearchResultResponse | null;
}

/**
 * v2 results: one tab per container size, best / fastest / price-range cards, a
 * filter panel, rows that open a three-group charge breakdown, and a tray to
 * export or copy the quotes you tick. Export uses the same workbook as Classic.
 */
export default function RateResults({ data }: RateResultsProps) {
  const [tab, setTab] = useState<string | null>(null);
  const [sort, setSort] = useState<SortKey>("price");
  const [hidden, setHidden] = useState<string[]>([]);
  const [hideSoldOut, setHideSoldOut] = useState(true);
  const [open, setOpen] = useState<string | null>(null);
  const [picked, setPicked] = useState<string[]>([]);
  const [details, setDetails] = useState<{ quote: QuoteSchema; carrier: string } | null>(null);

  const rows = useMemo<Row[]>(() => {
    if (!data) return [];
    return data.results.flatMap((cr) => {
      const meta = CARRIERS.find((c) => c.code === cr.carrier);
      return cr.quotes.map((q, i) => ({
        key: `${cr.carrier}:${i}`,
        carrier: cr.carrier,
        carrierName: meta?.name ?? cr.carrier,
        color: meta?.color ?? "currentColor",
        quote: q,
        size: q.container_type || "Other",
      }));
    });
  }, [data]);

  if (!data) return null;

  const sizes = Array.from(new Set(rows.map((r) => r.size))).sort(
    (a, b) => (SIZE_ORDER.indexOf(a) + 1 || 99) - (SIZE_ORDER.indexOf(b) + 1 || 99),
  );
  const activeSize = tab && sizes.includes(tab) ? tab : sizes[0];
  const inSize = rows.filter((r) => r.size === activeSize);

  const carrierCounts = new Map<string, { name: string; color: string; count: number }>();
  inSize.forEach((r) => {
    const c = carrierCounts.get(r.carrier) ?? { name: r.carrierName, color: r.color, count: 0 };
    c.count += 1;
    carrierCounts.set(r.carrier, c);
  });

  const visible = inSize
    .filter((r) => !hidden.includes(r.carrier) && !(hideSoldOut && isSoldOut(r.quote)))
    .sort((a, b) => {
      const qa = a.quote;
      const qb = b.quote;
      if (isSoldOut(qa) !== isSoldOut(qb)) return isSoldOut(qa) ? 1 : -1;
      if (sort === "transit") return (qa.transit_time_days || 999) - (qb.transit_time_days || 999) || qa.final_freight_value - qb.final_freight_value;
      if (sort === "departure") return dateValue(qa.etd) - dateValue(qb.etd) || qa.final_freight_value - qb.final_freight_value;
      return qa.final_freight_value - qb.final_freight_value;
    });

  const priced = visible.filter((r) => !isSoldOut(r.quote));
  const best = priced.reduce<Row | null>((m, r) => (!m || r.quote.final_freight_value < m.quote.final_freight_value ? r : m), null);
  const fastest = priced
    .filter((r) => r.quote.transit_time_days)
    .reduce<Row | null>((m, r) => (!m || r.quote.transit_time_days! < m.quote.transit_time_days! ? r : m), null);

  const ranges = new Map<string, { name: string; color: string; min: number; max: number }>();
  priced.forEach((r) => {
    const v = r.quote.final_freight_value;
    const g = ranges.get(r.carrier) ?? { name: r.carrierName, color: r.color, min: v, max: v };
    g.min = Math.min(g.min, v);
    g.max = Math.max(g.max, v);
    ranges.set(r.carrier, g);
  });
  const lo = priced.length ? Math.min(...priced.map((r) => r.quote.final_freight_value)) : 0;
  const hi = priced.length ? Math.max(...priced.map((r) => r.quote.final_freight_value)) : 0;
  const span = Math.max(1, hi - lo);
  const currency = priced[0]?.quote.currency ?? "USD";

  const noQuoteCarriers = data.results.filter(
    (cr) => cr.quotes.length === 0 && !RUNNING.has(cr.status) && !cr.status.startsWith("RUNNING"),
  );
  const pickedRows = rows.filter((r) => picked.includes(r.key));

  const togglePick = (key: string) =>
    setPicked((p) => (p.includes(key) ? p.filter((k) => k !== key) : [...p, key]));
  const toggleCarrier = (code: string) =>
    setHidden((h) => (h.includes(code) ? h.filter((c) => c !== code) : [...h, code]));

  /** The same workbook as Classic, limited to the given rows (carriers without any are left out). */
  const exportRows = async (subset: Row[] | null) => {
    const { exportSingleSearchToExcel } = await import("@/lib/excelExport");
    const results = subset
      ? data.results
          .map((cr) => ({ ...cr, quotes: cr.quotes.filter((_, i) => subset.some((r) => r.key === `${cr.carrier}:${i}`)) }))
          .filter((cr) => cr.quotes.length > 0)
      : data.results.filter((cr) => !hidden.includes(cr.carrier));
    await exportSingleSearchToExcel({ ...data, results });
  };

  const copyForEmail = async () => {
    const header = ["Carrier", "Size", "Departs", "Transit", "Free time", "Routing", "All-in"];
    const lines = pickedRows.map((r) => [
      r.carrierName,
      containerLabel(r.size),
      formatQuoteDate(r.quote.etd),
      r.quote.transit_time_days ? `${r.quote.transit_time_days} days` : "—",
      freeTimeText(r.quote),
      r.quote.port_of_discharge || r.quote.routing || "—",
      isSoldOut(r.quote) ? "Sold out" : money(r.quote.final_freight_value, r.quote.currency),
    ]);
    const esc = (v: string) => v.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    const html =
      `<table border="1" cellpadding="6" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px">` +
      `<tr>${header.map((h) => `<th style="background:#f0f2f5;text-align:left">${esc(h)}</th>`).join("")}</tr>` +
      lines.map((l) => `<tr>${l.map((v) => `<td>${esc(v)}</td>`).join("")}</tr>`).join("") +
      `</table>`;
    const text = [header, ...lines].map((l) => l.join("\t")).join("\n");
    try {
      await navigator.clipboard.write([
        new ClipboardItem({ "text/html": new Blob([html], { type: "text/html" }), "text/plain": new Blob([text], { type: "text/plain" }) }),
      ]);
    } catch {
      await navigator.clipboard.writeText(text);
    }
    toast.success(`Copied ${pickedRows.length} quote${pickedRows.length === 1 ? "" : "s"}: paste into your email`);
  };

  const sizesRequested = data.container_types ?? (data.container_type ? [data.container_type] : []);

  return (
    <section aria-labelledby="results-h" className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 id="results-h" className="flex flex-wrap items-center gap-2 text-lg font-bold text-foreground">
            {data.origin ?? "Origin"} <MoveRight className="size-4 text-muted-foreground" aria-hidden /> {data.destination ?? "Destination"}
          </h2>
          <p className="text-xs text-muted-foreground">
            {sizesRequested.map(containerLabel).join(", ")} · {rows.length} quote{rows.length === 1 ? "" : "s"} from{" "}
            {new Set(rows.map((r) => r.carrier)).size} carrier{new Set(rows.map((r) => r.carrier)).size === 1 ? "" : "s"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {sizes.length > 1 && (
            <div role="tablist" aria-label="Container size" className="flex flex-wrap gap-0.5 rounded-lg bg-secondary p-0.5">
              {sizes.map((s) => {
                const on = s === activeSize;
                return (
                  <button
                    key={s}
                    type="button"
                    role="tab"
                    aria-selected={on}
                    onClick={() => setTab(s)}
                    className={cn(
                      "min-h-9 rounded-md px-3 text-sm font-semibold transition-colors",
                      on ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground",
                    )}
                  >
                    {containerLabel(s)} <span className="font-medium opacity-70">{rows.filter((r) => r.size === s).length}</span>
                  </button>
                );
              })}
            </div>
          )}
          {rows.length > 0 && (
            <Button variant="outline" onClick={() => exportRows(null)}>
              <Download className="size-4" />
              Export to Excel
            </Button>
          )}
        </div>
      </div>

      {data.results.some((cr) => cr.has_port_mismatch === true) && (
        <Card variant="warning" className="flex items-start gap-3 p-4 text-xs text-warning-foreground">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div className="space-y-1">
            <p className="text-sm font-semibold">A carrier matched a different port than requested</p>
            {data.results
              .filter((cr) => cr.has_port_mismatch === true)
              .map((cr) => (
                <p key={cr.carrier}>
                  <strong>{CARRIERS.find((c) => c.code === cr.carrier)?.name ?? cr.carrier}:</strong>{" "}
                  {cr.mismatch_warning || "matched a different port."}
                </p>
              ))}
          </div>
        </Card>
      )}

      {rows.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Card className="p-4">
            <p className="text-xs font-semibold text-muted-foreground">Best all-in</p>
            <p className="text-2xl font-bold text-foreground">{best ? money(best.quote.final_freight_value, best.quote.currency) : "—"}</p>
            <p className="text-xs text-muted-foreground">{best ? `${best.carrierName} · departs ${formatQuoteDate(best.quote.etd)}` : "No priced quotes"}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs font-semibold text-muted-foreground">Fastest</p>
            <p className="text-2xl font-bold text-foreground">{fastest ? `${fastest.quote.transit_time_days} days` : "—"}</p>
            <p className="text-xs text-muted-foreground">
              {fastest ? `${fastest.carrierName} · ${money(fastest.quote.final_freight_value, fastest.quote.currency)}` : "No transit times"}
            </p>
          </Card>
          <Card className="p-4 sm:col-span-2">
            <div className="flex justify-between text-xs font-semibold text-muted-foreground">
              <span>Price range by carrier</span>
              {priced.length > 0 && <span>{money(lo, currency)} – {money(hi, currency)}</span>}
            </div>
            <ul className="mt-2 flex flex-col gap-1.5">
              {[...ranges.entries()]
                .sort((a, b) => a[1].min - b[1].min)
                .map(([code, g]) => (
                  <li key={code} className="grid grid-cols-[6rem_1fr_7rem] items-center gap-2 text-xs">
                    <span className="truncate font-semibold text-foreground">{g.name}</span>
                    <span className="relative h-2 rounded-full bg-secondary" aria-hidden>
                      <span
                        className="absolute inset-y-0 rounded-full ring-1 ring-foreground/20"
                        style={{
                          left: `${((g.min - lo) / span) * 92}%`,
                          width: `${Math.max(4, ((g.max - g.min) / span) * 92)}%`,
                          backgroundColor: g.color,
                        }}
                      />
                    </span>
                    <span className="text-right tabular-nums text-muted-foreground">
                      {g.min === g.max ? g.min.toLocaleString("en-US") : `${g.min.toLocaleString("en-US")}–${g.max.toLocaleString("en-US")}`}
                    </span>
                  </li>
                ))}
            </ul>
          </Card>
        </div>
      )}

      <div className="flex flex-wrap items-start gap-4">
        {rows.length > 0 && (
          <Card className="flex max-w-full flex-[1_1_15rem] flex-col gap-5 p-4">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Sort by</p>
              <div className="flex flex-col gap-1">
                {(
                  [
                    ["price", "Cheapest all-in"],
                    ["transit", "Fastest transit"],
                    ["departure", "Earliest departure"],
                  ] as const
                ).map(([id, label]) => (
                  <button
                    key={id}
                    type="button"
                    aria-pressed={sort === id}
                    onClick={() => setSort(id)}
                    className={cn(
                      "min-h-10 rounded-lg px-3 text-left text-sm transition-colors",
                      sort === id ? "bg-primary/10 font-semibold text-primary" : "text-foreground hover:bg-accent",
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Show carriers</p>
              <div className="flex flex-col gap-0.5">
                {[...carrierCounts.entries()].map(([code, c]) => {
                  const on = !hidden.includes(code);
                  return (
                    <button
                      key={code}
                      type="button"
                      aria-pressed={on}
                      onClick={() => toggleCarrier(code)}
                      className="flex min-h-10 items-center gap-2.5 rounded-lg px-1 text-left text-sm hover:bg-accent"
                    >
                      <span
                        className={cn(
                          "flex size-4.5 shrink-0 items-center justify-center rounded border-[1.5px]",
                          on ? "border-primary bg-primary text-primary-foreground" : "border-input bg-card",
                        )}
                      >
                        {on && <Check className="size-3" strokeWidth={3.5} />}
                      </span>
                      <span className="size-2 shrink-0 rounded-full ring-1 ring-foreground/20" style={{ backgroundColor: c.color }} aria-hidden />
                      <span className="flex-1 font-medium text-foreground">{c.name}</span>
                      <span className="text-xs text-muted-foreground">{c.count}</span>
                    </button>
                  );
                })}
              </div>
            </div>
            <button
              type="button"
              aria-pressed={hideSoldOut}
              onClick={() => setHideSoldOut((v) => !v)}
              className="flex min-h-10 items-center justify-between gap-3 text-left text-sm font-medium text-foreground"
            >
              Hide sold-out sailings
              <span className={cn("relative h-5 w-9 shrink-0 rounded-full transition-colors", hideSoldOut ? "bg-primary" : "bg-input")}>
                <span className={cn("absolute top-0.5 size-4 rounded-full bg-card transition-[left]", hideSoldOut ? "left-4.5" : "left-0.5")} />
              </span>
            </button>
            <p className="rounded-lg bg-muted p-3 text-xs text-muted-foreground">
              All-in = ocean freight + freight surcharges. Origin and destination charges are listed in each breakdown but not added.
            </p>
          </Card>
        )}

        <div className="flex min-w-0 flex-[999_1_40rem] flex-col gap-3">
          {rows.length > 0 && (
            <Card className="overflow-hidden p-0">
              <div className="overflow-x-auto">
                <div className="min-w-[56rem]">
                  <div className="grid grid-cols-[3rem_9rem_minmax(14rem,2fr)_7rem_5rem_8rem_9rem_3.25rem] items-center gap-x-3 border-b border-border bg-muted px-4 py-2.5 text-xs font-semibold text-muted-foreground">
                    <span>
                      <span className="sr-only">Select</span>
                    </span>
                    <span>Carrier</span>
                    <span>Routing</span>
                    <span>Departs</span>
                    <span>Transit</span>
                    <span>Free time</span>
                    <span className="text-right">All-in</span>
                    <span>
                      <span className="sr-only">Breakdown</span>
                    </span>
                  </div>
                  {visible.map((r) => {
                    const q = r.quote;
                    const isOpen = open === r.key;
                    const isPicked = picked.includes(r.key);
                    const isBest = best?.key === r.key;
                    const isFastest = fastest?.key === r.key && !isBest;
                    return (
                      <div key={r.key} className={cn("border-b border-border last:border-0", isPicked ? "bg-primary/5" : isOpen && "bg-muted/50")}>
                        <div className="grid grid-cols-[3rem_9rem_minmax(14rem,2fr)_7rem_5rem_8rem_9rem_3.25rem] items-center gap-x-3 px-4 py-2.5 text-sm">
                          <button
                            type="button"
                            aria-pressed={isPicked}
                            aria-label={`Select ${r.carrierName} ${formatQuoteDate(q.etd)}`}
                            onClick={() => togglePick(r.key)}
                            className="flex size-11 items-center justify-center"
                          >
                            <span
                              className={cn(
                                "flex size-5 items-center justify-center rounded border-[1.5px]",
                                isPicked ? "border-primary bg-primary text-primary-foreground" : "border-input bg-card",
                              )}
                            >
                              {isPicked && <Check className="size-3" strokeWidth={3.5} />}
                            </span>
                          </button>
                          <div className="min-w-0">
                            <p className="flex items-center gap-2 font-semibold text-foreground">
                              <span className="size-2.5 shrink-0 rounded-full ring-1 ring-foreground/15" style={{ backgroundColor: r.color }} aria-hidden />
                              <span className="truncate">{r.carrierName}</span>
                            </p>
                            <p className="text-[11px] text-muted-foreground">via {q.source === "carrier_api" ? "API" : "portal"}</p>
                          </div>
                          <div className="min-w-0">
                            <p className="truncate font-medium text-foreground">{q.port_of_discharge || q.routing || "—"}</p>
                            <p className="truncate text-xs text-muted-foreground">
                              {[q.service_name, q.vessel].filter(Boolean).join(" · ") || "—"}
                            </p>
                          </div>
                          <span className="text-foreground">{formatQuoteDate(q.etd)}</span>
                          <span className="text-foreground">{q.transit_time_days ? `${q.transit_time_days} d` : "—"}</span>
                          <span className="text-xs text-foreground">{freeTimeText(q)}</span>
                          <div className="text-right">
                            {isSoldOut(q) ? (
                              <span className="text-xs font-semibold text-destructive-foreground">{r.carrier === "OOCL" ? "Offline rates" : "Sold out"}</span>
                            ) : (
                              <>
                                <p className={cn("font-bold tabular-nums", isBest ? "text-warning-foreground" : "text-foreground")}>
                                  {money(q.final_freight_value, q.currency)}
                                </p>
                                <div className="flex flex-wrap justify-end gap-1">
                                  {isBest && <span className="rounded bg-warning/15 px-1.5 text-[11px] font-bold text-warning-foreground">Best price</span>}
                                  {isFastest && <span className="rounded bg-primary/10 px-1.5 text-[11px] font-bold text-primary">Fastest</span>}
                                  {isSpot(q) && <span className="rounded bg-secondary px-1.5 text-[11px] font-semibold text-muted-foreground">Spot</span>}
                                </div>
                              </>
                            )}
                          </div>
                          <Button
                            variant="outline"
                            size="icon"
                            aria-expanded={isOpen}
                            aria-label={`${isOpen ? "Hide" : "Show"} charges for ${r.carrierName} ${formatQuoteDate(q.etd)}`}
                            onClick={() => setOpen(isOpen ? null : r.key)}
                            className="size-11"
                          >
                            <ChevronDown className={cn("size-4 transition-transform", isOpen && "rotate-180")} />
                          </Button>
                        </div>
                        {isOpen && <Breakdown q={q} onDetails={() => setDetails({ quote: q, carrier: r.carrier })} />}
                      </div>
                    );
                  })}
                  {visible.length === 0 && (
                    <p className="px-4 py-8 text-center text-sm text-muted-foreground">
                      No quotes match these filters. Show more carriers or turn off &ldquo;Hide sold-out sailings&rdquo;.
                    </p>
                  )}
                </div>
              </div>
            </Card>
          )}

          {noQuoteCarriers.length > 0 && (
            <Card variant="subtle" className="p-4 text-sm">
              <p className="mb-2 text-xs font-semibold text-muted-foreground">No quotes from</p>
              <ul className="flex flex-col gap-1">
                {noQuoteCarriers.map((cr) => (
                  <li key={cr.carrier} className="flex flex-wrap gap-x-2">
                    <span className="font-semibold text-foreground">{CARRIERS.find((c) => c.code === cr.carrier)?.name ?? cr.carrier}</span>
                    <span className="text-muted-foreground">
                      {cr.error_message || (cr.status === "NO_QUOTES_AVAILABLE" ? "No quotes on this lane" : cr.status.replace(/_/g, " ").toLowerCase())}
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </div>

      {pickedRows.length > 0 && (
        <div className="sticky bottom-4 z-10">
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-foreground px-4 py-3 text-background shadow-card">
            <span className="font-semibold">
              {pickedRows.length} quote{pickedRows.length === 1 ? "" : "s"} selected for the customer quotation
            </span>
            <div className="flex flex-wrap gap-2">
              <Button variant="ghost" className="text-background hover:bg-background/15 hover:text-background" onClick={() => setPicked([])}>
                <X className="size-4" />
                Clear
              </Button>
              <Button variant="ghost" className="text-background hover:bg-background/15 hover:text-background" onClick={copyForEmail}>
                <ClipboardCopy className="size-4" />
                Copy as email table
              </Button>
              <Button className="bg-background text-foreground hover:bg-background/90" onClick={() => exportRows(pickedRows)}>
                <Download className="size-4" />
                Export selected
              </Button>
            </div>
          </div>
        </div>
      )}

      <QuoteBreakdownDrawer quote={details?.quote || null} carrier={details?.carrier || ""} onClose={() => setDetails(null)} />
    </section>
  );
}
