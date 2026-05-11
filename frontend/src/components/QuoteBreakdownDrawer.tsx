"use client";
import type { QuoteSchema, ChargeSchema } from "@/lib/types";

interface QuoteBreakdownDrawerProps {
  quote: QuoteSchema | null;
  carrier: string;
  onClose: () => void;
}

function ChargeTable({ title, charges, color }: { title: string; charges: ChargeSchema[]; color: string }) {
  if (charges.length === 0) return null;
  return (
    <div className="space-y-2">
      <h4 className={`text-sm font-semibold ${color}`}>{title}</h4>
      <div className="bg-white/5 rounded-xl overflow-hidden">
        {charges.map((ch, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5 border-b border-white/5 last:border-0">
            <div className="flex-1">
              <span className="text-sm text-white/80">{ch.name}</span>
              {ch.reason && <span className="block text-xs text-white/40 mt-0.5">{ch.reason}</span>}
            </div>
            <span className={`text-sm font-mono font-medium ${ch.amount < 0 ? "text-red-400" : "text-white/80"}`}>
              {ch.currency} {ch.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function QuoteBreakdownDrawer({ quote, carrier, onClose }: QuoteBreakdownDrawerProps) {
  if (!quote) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full max-w-lg bg-[#0a0e1a] border-l border-white/10 z-50 overflow-y-auto animate-slide-in">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">Quote Breakdown</h3>
              <p className="text-sm text-white/50">{carrier} • {quote.service_name || "N/A"}</p>
            </div>
            <button onClick={onClose} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-white transition-all">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Route & Schedule */}
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "ETD", value: quote.etd || "—" },
              { label: "ETA", value: quote.eta || "—" },
              { label: "Transit", value: quote.transit_time_days ? `${quote.transit_time_days} days` : "—" },
              { label: "Vessel", value: quote.vessel || "—" },
              { label: "Container", value: quote.container_type || "—" },
              { label: "Source", value: quote.source },
            ].map((item, i) => (
              <div key={i} className="bg-white/5 rounded-lg px-3 py-2">
                <span className="block text-xs text-white/40">{item.label}</span>
                <span className="block text-sm text-white/80 font-medium">{item.value}</span>
              </div>
            ))}
          </div>

          {/* Final Freight Value */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl px-5 py-4">
            <span className="block text-xs text-blue-300/80 uppercase tracking-wider font-medium">Final Freight Value</span>
            <span className="block text-3xl font-bold text-white mt-1">
              {quote.currency} {quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="block text-xs text-white/40 mt-1">
              BOF ({quote.basic_ocean_freight.toLocaleString()}) + Discount ({quote.discount.toLocaleString()}) + Surcharges
            </span>
          </div>

          {/* Ocean Freight & Discount */}
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-emerald-400">Ocean Freight</h4>
            <div className="bg-white/5 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/5">
                <span className="text-sm text-white/80">Basic Ocean Freight</span>
                <span className="text-sm font-mono font-medium text-white/80">
                  {quote.currency} {quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              {quote.discount !== 0 && (
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-white/80">Discount / Rebate</span>
                  <span className="text-sm font-mono font-medium text-red-400">
                    {quote.currency} {quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Freight Surcharges (Included) */}
          <ChargeTable title="Freight Surcharges (Included in Final Value)" charges={quote.included_freight_surcharges} color="text-blue-400" />

          {/* Excluded Charges */}
          <ChargeTable title="Origin & Destination Charges (Excluded)" charges={quote.excluded_charges} color="text-yellow-400" />

          {/* Uncertain Charges */}
          <ChargeTable title="Uncertain Charges (Excluded)" charges={quote.uncertain_charges} color="text-orange-400" />
        </div>
      </div>
    </>
  );
}
