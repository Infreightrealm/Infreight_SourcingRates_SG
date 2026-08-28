"use client";
import { useState } from "react";
import type { RateSearchResultResponse, QuoteSchema } from "@/lib/types";
import { CARRIERS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";
import { Download, Inbox } from "lucide-react";

function formatDate(dateVal: string | null | undefined): string {
  if (!dateVal || dateVal === "—" || dateVal === "-") return "—";
  const dateStr = dateVal.trim();
  if (!dateStr) return "—";

  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  // Check for ISO format: YYYY-MM-DD
  const matchISO = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})(?:T.*)?$/);
  if (matchISO) {
    const year = parseInt(matchISO[1], 10);
    const month = parseInt(matchISO[2], 10);
    const day = parseInt(matchISO[3], 10);
    if (month >= 1 && month <= 12) {
      return `${day} ${months[month - 1]} ${year}`;
    }
  }

  // Check for DD-Mon-YYYY or DD Mon YYYY
  const matchAbbr = dateStr.match(/^(\d{1,2})[ \-/\\]([A-Za-z]{3})[ \-/\\](\d{4})$/);
  if (matchAbbr) {
    const day = parseInt(matchAbbr[1], 10);
    const monthStr = matchAbbr[2];
    const year = matchAbbr[3];
    const formattedMonth = monthStr.charAt(0).toUpperCase() + monthStr.slice(1).toLowerCase();
    return `${day} ${formattedMonth} ${year}`;
  }

  // Generic Date parsing fallback
  const matchSlash = dateStr.match(/^(\d{4})\/(\d{2})\/(\d{2})$/);
  if (matchSlash) {
    const year = parseInt(matchSlash[1], 10);
    const month = parseInt(matchSlash[2], 10);
    const day = parseInt(matchSlash[3], 10);
    if (month >= 1 && month <= 12) {
      return `${day} ${months[month - 1]} ${year}`;
    }
  }

  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    if (!dateStr.includes("T") && !dateStr.includes(" ")) {
      return `${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
    }
    return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
  }

  return dateStr;
}

interface ResultsTableProps {
  data: RateSearchResultResponse | null;
}

export default function ResultsTable({ data }: ResultsTableProps) {
  const [selectedQuote, setSelectedQuote] = useState<{ quote: QuoteSchema; carrier: string } | null>(null);
  const [sortBy, setSortBy] = useState<"freight" | "etd" | "transit">("freight");
  const [containerFilter, setContainerFilter] = useState<string>("ALL");

  if (!data) return null;

  // Flatten all quotes from all carriers into one table
  const allRows: {
    carrier: string;
    carrierColor: string;
    status: string;
    error?: string;
    quote?: QuoteSchema;
    hasPortMismatch?: boolean | null;
    mismatchWarning?: string;
  }[] = [];

  for (const cr of data.results) {
    const carrierInfo = CARRIERS.find((c) => c.code === cr.carrier);
    const color = carrierInfo?.color || "#666";
    
    // If quotes are present, status is AVAILABLE_QUOTES_FOUND regardless of transient errors; normalize MSC Timeout
    let status = cr.quotes.length > 0 ? "AVAILABLE_QUOTES_FOUND" : cr.status;
    if (cr.carrier === "MSC" && status === "TIMEOUT") {
      status = "NO_QUOTES_AVAILABLE";
    }

    if (cr.quotes.length === 0) {
      allRows.push({
        carrier: cr.carrier,
        carrierColor: color,
        status: status,
        error: cr.error_message,
        hasPortMismatch: cr.has_port_mismatch,
        mismatchWarning: cr.mismatch_warning,
      });
    } else {
      for (const q of cr.quotes) {
        allRows.push({
          carrier: cr.carrier,
          carrierColor: color,
          status: status,
          quote: q,
          hasPortMismatch: cr.has_port_mismatch,
          mismatchWarning: cr.mismatch_warning,
        });
      }
    }
  }

  const quoteRows = allRows.filter((r) => r.quote);
  const nonQuoteRows = allRows.filter((r) => !r.quote);


  const CONTAINER_ORDER: Record<string, number> = {
    "DRY 20": 1, "20GP": 1, "20'": 1,
    "DRY 40": 2, "40GP": 2, "40'": 2,
    "DRY 40H": 3, "40HQ": 3, "40HC": 3, "40'HQ": 3, "40'HC": 3,
  };

  const sortContainerTypes = (types: string[]): string[] => {
    return [...types].sort((a, b) => {
      const orderA = CONTAINER_ORDER[a.toUpperCase()] ?? 99;
      const orderB = CONTAINER_ORDER[b.toUpperCase()] ?? 99;
      if (orderA !== orderB) return orderA - orderB;
      return a.localeCompare(b);
    });
  };

  const uniqueContainerTypes = sortContainerTypes(
    Array.from(
      new Set(
        quoteRows
          .map((r) => r.quote?.container_type)
          .filter((ct): ct is string => !!ct)
      )
    )
  );

  const getContainerDisplayName = (type: string) => {
    if (type === "DRY 20") return "20GP";
    if (type === "DRY 40") return "40GP";
    if (type === "DRY 40H") return "40HQ";
    return type;
  };

  const filteredQuoteRows = quoteRows.filter((r) => {
    if (!r.quote) return false;
    if (containerFilter === "ALL") return true;
    return r.quote.container_type === containerFilter;
  });

  filteredQuoteRows.sort((a, b) => {
    if (!a.quote || !b.quote) return 0;
    if (sortBy === "freight") return a.quote.final_freight_value - b.quote.final_freight_value;
    if (sortBy === "etd") return (a.quote.etd || "").localeCompare(b.quote.etd || "");
    if (sortBy === "transit") return (a.quote.transit_time_days || 99) - (b.quote.transit_time_days || 99);
    return 0;
  });

  const sortedRows = [...filteredQuoteRows, ...nonQuoteRows];

  const surchargeTotal = (q: QuoteSchema) =>
    q.included_freight_surcharges.reduce((s, c) => s + c.amount, 0);

  const exportToExcel = async () => {
    if (!data) return;
    const { exportMultiRouteResultsToExcel } = await import("@/lib/excelExport");
    const safeOrig = (data.origin || "Origin").replace(/[^a-zA-Z0-9]/g, "_");
    const safeDest = (data.destination || "Destination").replace(/[^a-zA-Z0-9]/g, "_");
    await exportMultiRouteResultsToExcel(
      [
        {
          origin: data.origin || "",
          destination: data.destination || "",
          status: "completed",
          searchResult: data,
        },
      ],
      `Infreight_${safeOrig}_to_${safeDest}_Rates.xlsx`
    );
  };

  return (
    <>
      <div className="space-y-4 animate-fade-in-up">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Search Results
              {data.origin && data.destination && (
                <span className="text-slate-500 dark:text-white/50 font-normal text-sm ml-2">
                  {data.origin} → {data.destination}
                </span>
              )}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <StatusBadge status={data.status} size="md" />
              <div className="flex gap-1.5 flex-wrap">
                {sortContainerTypes(data.container_types || (data.container_type ? [data.container_type] : [])).map((ct) => (
                  <span key={ct} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-white/70">
                    {ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct} × {data.container_quantity}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 w-full sm:w-auto">
            {/* Container Type Filter */}
            {uniqueContainerTypes.length > 1 && (
              <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                <span className="text-xs text-slate-500 dark:text-white/40">Container:</span>
                <button
                  onClick={() => setContainerFilter("ALL")}
                  className={`px-3 py-1.5 min-h-[36px] sm:min-h-[44px] flex items-center justify-center rounded-lg text-xs font-medium btn-interactive transition-all ${
                    containerFilter === "ALL"
                      ? "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-600/30 dark:text-blue-300 border dark:border-blue-500/30"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent dark:bg-white/5 dark:text-white/50 dark:hover:text-white/70"
                  }`}
                >
                  All
                </button>
                {uniqueContainerTypes.map((ct) => (
                  <button
                    key={ct}
                    onClick={() => setContainerFilter(ct)}
                    className={`px-3 py-1.5 min-h-[36px] sm:min-h-[44px] flex items-center justify-center rounded-lg text-xs font-medium btn-interactive transition-all ${
                      containerFilter === ct
                        ? "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-600/30 dark:text-blue-300 border dark:border-blue-500/30"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent dark:bg-white/5 dark:text-white/50 dark:hover:text-white/70"
                    }`}
                  >
                    {getContainerDisplayName(ct)}
                  </button>
                ))}
              </div>
            )}

            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <span className="text-xs text-slate-500 dark:text-white/40">Sort by:</span>
              {(["freight", "etd", "transit"] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`px-3 py-1.5 min-h-[36px] sm:min-h-[44px] flex items-center justify-center rounded-lg text-xs font-medium btn-interactive transition-all ${
                    sortBy === key 
                      ? "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-600/30 dark:text-blue-300 border dark:border-blue-500/30" 
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent dark:bg-white/5 dark:text-white/50 dark:hover:text-white/70"
                  }`}
                >
                  {key === "freight" ? "💰 Price" : key === "etd" ? "📅 ETD" : "⏱ Transit"}
                </button>
              ))}
            </div>
            
            {quoteRows.length > 0 && (
              <button
                onClick={exportToExcel}
                className="flex items-center justify-center gap-1.5 px-3.5 py-2 min-h-[44px] rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 dark:border-white/10 transition-colors btn-interactive shine-on-hover"
              >
                <Download className="w-3.5 h-3.5" />
                Export Excel
              </button>
            )}
          </div>
        </div>

        {/* Mismatch Warning Banner */}
        {data.results.some((cr) => cr.has_port_mismatch === true) && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 text-amber-900 dark:text-amber-300 text-xs flex items-start gap-3 shadow-sm animate-in fade-in duration-300">
            <span className="text-lg leading-none">⚠️</span>
            <div className="space-y-1">
              <p className="font-bold text-sm">Port Selection Mismatch Warning</p>
              <p className="text-slate-600 dark:text-amber-400/90">The carrier matched a port that differs from your requested port location. Please review:</p>
              <div className="mt-2 space-y-1">
                {data.results.filter((cr) => cr.has_port_mismatch === true).map((cr) => (
                  <div key={cr.carrier} className="font-mono text-[11px] bg-amber-500/10 px-2.5 py-1 rounded-lg">
                    <strong className="font-semibold">{cr.carrier.replace("_", " ")}:</strong> {cr.mismatch_warning || "Carrier matched a different port than requested."}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Table / Empty State */}
        {sortedRows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white/50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-2xl">
            <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4 animate-float">
              <Inbox className="w-8 h-8 text-slate-400 dark:text-white/30" />
            </div>
            <div className="animate-fade-in-up">
              <h3 className="text-slate-700 dark:text-white/80 font-medium text-lg">No Results Found</h3>
              <p className="text-slate-500 dark:text-white/40 text-sm mt-1">Try adjusting your search parameters or selecting different carriers.</p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] max-h-[600px] overflow-y-auto w-full max-w-full">

            <table className="w-full text-xs relative">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#1a1f2e] backdrop-blur-md">
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Carrier</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Status</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Container</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">ETD POL</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">ETA POD</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Validity</th>

                  <th className="px-1 py-2 text-center text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Transit</th>
                  <th className="px-1 py-2 text-center text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Free Time</th>
                  <th className="px-1 py-2 text-center text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Demurrage</th>
                  <th className="px-1 py-2 text-center text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Detention</th>
                  <th className="px-1 py-2 text-left text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Service / Vessel</th>
                  <th className="px-1 py-2 text-right text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">BOF</th>
                  <th className="px-1 py-2 text-right text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Discount</th>
                  <th className="px-1 py-2 text-right text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Surcharges</th>
                  <th className="px-1 py-2 text-right text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Final Value</th>
                  <th className="px-1 py-2 text-center text-[11px] font-semibold text-slate-600 dark:text-white/60 whitespace-nowrap">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedRows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-all duration-200 hover:-translate-y-[1px] row-enter" style={{animationDelay: `${i * 0.04}s`}}>
                    {/* Carrier */}
                    <td className="px-1 py-2">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: row.carrierColor }} />
                        <span className="font-medium text-slate-900 dark:text-white/90">{row.carrier.replace("_", " ")}</span>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-1 py-2">
                      <div className="flex flex-col gap-1">
                        <StatusBadge status={row.status} />
                        {row.hasPortMismatch === true && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/10 px-1.5 py-0.5 rounded" title={row.mismatchWarning || "Port Mismatch"}>
                            ⚠️ Mismatch
                          </span>
                        )}
                      </div>
                    </td>


                    {row.quote ? (
                      <>
                        {/* Container */}
                        <td className="px-1 py-2">
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-800 dark:bg-white/10 dark:text-white/80">
                            {row.quote.container_type === "DRY 20" ? "20GP" : row.quote.container_type === "DRY 40" ? "40GP" : row.quote.container_type === "DRY 40H" ? "40HQ" : row.quote.container_type || "—"}
                          </span>
                        </td>
                        <td className="px-1 py-2 text-slate-600 dark:text-white/70 font-mono text-[11px] whitespace-nowrap">{formatDate(row.quote.etd)}</td>
                        <td className="px-1 py-2 text-slate-600 dark:text-white/70 font-mono text-[11px] whitespace-nowrap">{formatDate(row.quote.eta)}</td>
                        <td className="px-1 py-2 text-slate-600 dark:text-white/70 font-mono text-[11px] whitespace-nowrap">{formatDate(row.quote.validity_till)}</td>
                        <td className="px-1 py-2 text-center text-slate-600 dark:text-white/70 whitespace-nowrap">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                        <td className="px-1 py-2 text-center">
                          {row.quote.free_time != null ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                              {String(row.quote.free_time).endsWith("d") || String(row.quote.free_time).includes(" ") ? row.quote.free_time : `${row.quote.free_time}d`}
                            </span>
                          ) : <span className="text-slate-400 dark:text-white/25 text-[11px]">—</span>}
                        </td>
                        <td className="px-1 py-2 text-center font-mono text-[11px]">
                          {row.quote.demurrage ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
                              {row.quote.demurrage}d
                            </span>
                          ) : <span className="text-slate-400 dark:text-white/25 text-[11px]">—</span>}
                        </td>
                        <td className="px-1 py-2 text-center font-mono text-[11px]">
                          {row.quote.detention ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
                              {row.quote.detention}d
                            </span>
                          ) : <span className="text-slate-400 dark:text-white/25 text-[11px]">—</span>}
                        </td>
                        <td className="px-1 py-2">
                          <div className="text-slate-700 dark:text-white/70 text-[11px] font-medium leading-tight">{row.quote.service_name || "—"}</div>
                          <div className="text-slate-500 dark:text-white/40 text-[10px] leading-none mt-0.5">{row.quote.vessel || ""}</div>
                        </td>
                        <td className="px-1 py-2 text-right font-mono text-slate-700 dark:text-white/80">
                          {row.quote.final_freight_value === 0.0 ? "—" : row.quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-1 py-2 text-right font-mono text-red-600 dark:text-red-400">
                          {row.quote.discount !== 0 ? row.quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                        </td>
                        <td className="px-1 py-2 text-right font-mono text-blue-600 dark:text-blue-300">
                          {row.quote.final_freight_value === 0.0 ? "—" : surchargeTotal(row.quote).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-1 py-2 text-right">
                          {row.quote.final_freight_value === 0.0 ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400">
                              {row.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold Out"}
                            </span>
                          ) : (
                            <>
                              <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                                {row.quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                              </span>
                              <span className="block text-[10px] text-slate-500 dark:text-white/40 leading-none">{row.quote.currency}</span>
                            </>
                          )}
                        </td>
                        <td className="px-1 py-2 text-center">
                          {row.quote.final_freight_value === 0.0 ? (
                            <button
                              disabled
                              className="px-2 py-1 rounded bg-slate-100 text-slate-400 dark:bg-white/5 dark:text-white/20 text-[10px] font-medium cursor-not-allowed border border-transparent shadow-sm"
                            >
                              Unavailable
                            </button>
                          ) : (
                            <button
                              onClick={() => setSelectedQuote({ quote: row.quote!, carrier: row.carrier })}
                              className="px-2 py-1 rounded bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-600/20 dark:text-blue-300 text-[10px] font-medium dark:hover:bg-blue-600/30 border border-blue-200 dark:border-blue-500/20 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all shadow-sm"
                            >
                              View
                            </button>
                          )}
                        </td>
                      </>
                    ) : (
                      <td colSpan={12} className="px-1 py-2 text-[11px] text-center">
                        {row.status === "WAITING_FOR_HUMAN_VERIFICATION" ? (
                          <span className="text-amber-600 dark:text-amber-400 font-semibold animate-pulse">
                            ⚠️ Cloudflare Security Check / CAPTCHA: Solve in VNC tab to resume crawler
                          </span>
                        ) : (
                          <span className="text-slate-500 dark:text-white/40 italic">
                            {row.error || (row.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not yet implemented" : "No quotes returned")}
                          </span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Breakdown Drawer */}
      <QuoteBreakdownDrawer
        quote={selectedQuote?.quote || null}
        carrier={selectedQuote?.carrier || ""}
        onClose={() => setSelectedQuote(null)}
      />
    </>
  );
}
