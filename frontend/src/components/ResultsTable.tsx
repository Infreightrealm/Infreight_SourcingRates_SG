"use client";
import { useState } from "react";
import type { RateSearchResultResponse, QuoteSchema } from "@/lib/types";
import { CARRIERS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";

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

  // Sort quote rows
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

  return (
    <>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">
              Search Results
              {data.origin && data.destination && (
                <span className="text-white/50 font-normal text-sm ml-2">
                  {data.origin} → {data.destination}
                </span>
              )}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <StatusBadge status={data.status} size="md" />
              {data.container_type && (
                <span className="text-xs text-white/40">{data.container_type} × {data.container_quantity}</span>
              )}
            </div>
          </div>

          {/* Sort Controls */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-white/40">Sort by:</span>
            {(["freight", "etd", "transit"] as const).map((key) => (
              <button
                key={key}
                onClick={() => setSortBy(key)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  sortBy === key ? "bg-blue-600/30 text-blue-300 border border-blue-500/30" : "bg-white/5 text-white/50 hover:text-white/70 border border-transparent"
                }`}
              >
                {key === "freight" ? "💰 Price" : key === "etd" ? "📅 ETD" : "⏱ Transit"}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.02]">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                <th className="px-4 py-3 text-left text-xs font-semibold text-white/60 uppercase tracking-wider">Carrier</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white/60 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white/60 uppercase tracking-wider">ETD</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white/60 uppercase tracking-wider">ETA</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-white/60 uppercase tracking-wider">Transit</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white/60 uppercase tracking-wider">Service / Vessel</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-white/60 uppercase tracking-wider">BOF</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-white/60 uppercase tracking-wider">Discount</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-white/60 uppercase tracking-wider">Surcharges</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-white/60 uppercase tracking-wider">Final Value</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-white/60 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedRows.map((row, i) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
                  {/* Carrier */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: row.carrierColor }} />
                      <span className="font-medium text-white/90">{row.carrier.replace("_", " ")}</span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <StatusBadge status={row.status} />
                  </td>

                  {row.quote ? (
                    <>
                      <td className="px-4 py-3 text-white/70 font-mono text-xs">{row.quote.etd || "—"}</td>
                      <td className="px-4 py-3 text-white/70 font-mono text-xs">{row.quote.eta || "—"}</td>
                      <td className="px-4 py-3 text-center text-white/70">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                      <td className="px-4 py-3">
                        <div className="text-white/70 text-xs">{row.quote.service_name || "—"}</div>
                        <div className="text-white/40 text-xs">{row.quote.vessel || ""}</div>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-white/80">
                        {row.quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-red-400">
                        {row.quote.discount !== 0 ? row.quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-blue-300">
                        {surchargeTotal(row.quote).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="font-mono font-bold text-emerald-400 text-base">
                          {row.quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        <span className="block text-xs text-white/40">{row.quote.currency}</span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => setSelectedQuote({ quote: row.quote!, carrier: row.carrier })}
                          className="px-3 py-1.5 rounded-lg bg-blue-600/20 text-blue-300 text-xs font-medium hover:bg-blue-600/30 border border-blue-500/20 hover:border-blue-500/40 transition-all"
                        >
                          View
                        </button>
                      </td>
                    </>
                  ) : (
                    <td colSpan={9} className="px-4 py-3 text-white/40 text-xs">
                      {row.error || (row.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not yet implemented" : "No quotes returned")}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
