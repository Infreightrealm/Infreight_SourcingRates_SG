"use client";
import { useState } from "react";
import type { RateSearchResultResponse, QuoteSchema } from "@/lib/types";
import { CARRIERS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";
import { Download, Inbox } from "lucide-react";

interface ResultsTableProps {
  data: RateSearchResultResponse | null;
}

export default function ResultsTable({ data }: ResultsTableProps) {
  const [selectedQuote, setSelectedQuote] = useState<{ quote: QuoteSchema; carrier: string } | null>(null);
  const [sortBy, setSortBy] = useState<"freight" | "etd" | "transit">("freight");

  if (!data) return null;

  // Flatten all quotes from all carriers into one table
  const allRows: { carrier: string; carrierColor: string; status: string; error?: string; quote?: QuoteSchema }[] = [];

  for (const cr of data.results) {
    const carrierInfo = CARRIERS.find((c) => c.code === cr.carrier);
    const color = carrierInfo?.color || "#666";

    if (cr.quotes.length === 0) {
      allRows.push({ carrier: cr.carrier, carrierColor: color, status: cr.status, error: cr.error_message });
    } else {
      for (const q of cr.quotes) {
        allRows.push({ carrier: cr.carrier, carrierColor: color, status: cr.status, quote: q });
      }
    }
  }

  const quoteRows = allRows.filter((r) => r.quote);
  const nonQuoteRows = allRows.filter((r) => !r.quote);

  quoteRows.sort((a, b) => {
    if (!a.quote || !b.quote) return 0;
    if (sortBy === "freight") return a.quote.final_freight_value - b.quote.final_freight_value;
    if (sortBy === "etd") return (a.quote.etd || "").localeCompare(b.quote.etd || "");
    if (sortBy === "transit") return (a.quote.transit_time_days || 99) - (b.quote.transit_time_days || 99);
    return 0;
  });

  const sortedRows = [...quoteRows, ...nonQuoteRows];

  const surchargeTotal = (q: QuoteSchema) =>
    q.included_freight_surcharges.reduce((s, c) => s + c.amount, 0);

  const exportToCSV = () => {
    if (quoteRows.length === 0) return;
    const headers = ["Carrier", "ETD", "ETA", "Transit (Days)", "Service/Vessel", "Basic Freight", "Discount", "Surcharges", "Final Value", "Currency"];
    const rows = quoteRows.map(r => [
      r.carrier,
      r.quote!.etd || "",
      r.quote!.eta || "",
      r.quote!.transit_time_days || "",
      `${r.quote!.service_name || ""} ${r.quote!.vessel || ""}`.trim(),
      r.quote!.basic_ocean_freight,
      r.quote!.discount,
      surchargeTotal(r.quote!),
      r.quote!.final_freight_value,
      r.quote!.currency
    ]);
    
    const csvContent = [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `rates_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="space-y-4">
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
              {data.container_type && (
                <span className="text-xs text-slate-500 dark:text-white/40">{data.container_type} × {data.container_quantity}</span>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 dark:text-white/40">Sort by:</span>
              {(["freight", "etd", "transit"] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
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
                onClick={exportToCSV}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 dark:border-white/10 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </button>
            )}
          </div>
        </div>

        {/* Table / Empty State */}
        {sortedRows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white/50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-2xl">
            <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4">
              <Inbox className="w-8 h-8 text-slate-400 dark:text-white/30" />
            </div>
            <h3 className="text-slate-700 dark:text-white/80 font-medium text-lg">No Results Found</h3>
            <p className="text-slate-500 dark:text-white/40 text-sm mt-1">Try adjusting your search parameters or selecting different carriers.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] max-h-[600px] overflow-y-auto">
            <table className="w-full text-sm relative">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#1a1f2e] backdrop-blur-md">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Carrier</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETD</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETA</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Transit</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Service / Vessel</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">BOF</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Discount</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Surcharges</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Final Value</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedRows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors">
                    {/* Carrier */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: row.carrierColor }} />
                        <span className="font-medium text-slate-900 dark:text-white/90">{row.carrier.replace("_", " ")}</span>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <StatusBadge status={row.status} />
                    </td>

                    {row.quote ? (
                      <>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.etd || "—"}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.eta || "—"}</td>
                        <td className="px-4 py-3 text-center text-slate-600 dark:text-white/70">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                        <td className="px-4 py-3">
                          <div className="text-slate-700 dark:text-white/70 text-xs font-medium">{row.quote.service_name || "—"}</div>
                          <div className="text-slate-500 dark:text-white/40 text-xs">{row.quote.vessel || ""}</div>
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-slate-700 dark:text-white/80">
                          {row.quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-red-600 dark:text-red-400">
                          {row.quote.discount !== 0 ? row.quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-blue-600 dark:text-blue-300">
                          {surchargeTotal(row.quote).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-base">
                            {row.quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </span>
                          <span className="block text-xs text-slate-500 dark:text-white/40">{row.quote.currency}</span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <button
                            onClick={() => setSelectedQuote({ quote: row.quote!, carrier: row.carrier })}
                            className="px-3 py-1.5 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-600/20 dark:text-blue-300 text-xs font-medium dark:hover:bg-blue-600/30 border border-blue-200 dark:border-blue-500/20 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all shadow-sm"
                          >
                            View
                          </button>
                        </td>
                      </>
                    ) : (
                      <td colSpan={9} className="px-4 py-3 text-slate-500 dark:text-white/40 text-xs text-center italic">
                        {row.error || (row.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not yet implemented" : "No quotes returned")}
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
