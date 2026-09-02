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
      <div className="bg-slate-100 dark:bg-white/5 rounded-xl overflow-hidden">
        {charges.map((ch, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5 border-b border-slate-200 dark:border-white/5 last:border-0">
            <div className="flex-1">
              <span className="text-sm text-slate-700 dark:text-white/80">{ch.name}</span>
              {ch.reason && <span className="block text-xs text-slate-500 dark:text-white/40 mt-0.5">{ch.reason}</span>}
            </div>
            <span className={`text-sm font-mono font-medium ${ch.amount < 0 ? "text-red-600 dark:text-red-400" : "text-slate-700 dark:text-white/80"}`}>
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
      <div className="fixed inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm z-40 animate-blur-in" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full max-w-lg bg-white dark:bg-[#0a0e1a] border-l border-slate-200 dark:border-white/10 z-50 overflow-y-auto animate-slide-in-spring">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Quote Breakdown</h3>
              <p className="text-sm text-slate-500 dark:text-white/50">{carrier} • {quote.service_name || "N/A"}</p>
            </div>
            <button onClick={onClose} className="p-2 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-500 dark:text-white/60 hover:text-slate-900 dark:hover:text-white transition-all btn-interactive">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Route & Schedule */}
          <div className="grid grid-cols-2 gap-3 animate-fade-in-up stagger-1">
            {[
              { label: "ETD", value: quote.etd || "—" },
              { label: "ETA", value: quote.eta || "—" },
              { label: "Transit", value: quote.transit_time_days ? `${quote.transit_time_days} days` : "—" },
              { label: "Free Time", value: quote.free_time != null ? `${quote.free_time} days` : "—" },
              { label: "Import Demurrage", value: quote.demurrage ? `${quote.demurrage} days` : "—" },
              { label: "Import Detention", value: quote.detention ? `${quote.detention} days` : "—" },
              { label: "Vessel", value: quote.vessel || "—" },
              { label: "Container", value: quote.container_type || "—" },
              { label: "Source", value: quote.source },
            ].map((item, i) => (
              <div key={i} className={`rounded-lg px-3 py-2 ${item.label.includes("Free Time") && quote.free_time != null ? "bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700/40" : "bg-slate-100 dark:bg-white/5"}`}>
                <span className={`block text-xs ${item.label.includes("Free Time") && quote.free_time != null ? "text-emerald-600 dark:text-emerald-400 font-semibold" : "text-slate-500 dark:text-white/40"}`}>{item.label}</span>
                <span className={`block text-sm font-medium ${item.label.includes("Free Time") && quote.free_time != null ? "text-emerald-700 dark:text-emerald-300" : "text-slate-700 dark:text-white/80"}`}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Breakdown Unavailable Warning Banner */}
          {quote.is_breakdown_unavailable && (
            <div className="bg-amber-500/15 border border-amber-500/40 rounded-2xl p-4 text-amber-900 dark:text-amber-300 text-xs flex items-start gap-3 shadow-sm animate-fade-in-up">
              <span className="text-xl leading-none">⚠️</span>
              <div className="space-y-1">
                <p className="font-bold text-sm text-amber-700 dark:text-amber-400">Quote Surcharges Incomplete</p>
                <p className="text-slate-700 dark:text-amber-200/90 leading-relaxed">
                  This quote cannot accurately provide the final freight value because the price breakdown is disabled on the carrier portal:
                </p>
                <div className="mt-1.5 p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 font-medium italic text-[11px] text-amber-800 dark:text-amber-300">
                  "{quote.warning_message || 'Some selected container types are currently unavailable for this sailing. Please update the container type or select another departure date.'}"
                </div>
                <p className="text-[11px] text-slate-500 dark:text-amber-400/80 mt-1">
                  * Line-item surcharges (ETS, EBS, Terminal Handling) could not be scraped. The value below reflects only the basic ocean rate.
                </p>
              </div>
            </div>
          )}

          {/* Final Freight Value */}
          <div className="bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-600/20 dark:to-purple-600/20 border border-blue-200 dark:border-blue-500/30 rounded-xl px-5 py-4 animate-fade-in-up stagger-2 animate-gradient-shift" style={{backgroundSize: "200% 200%"}}>
            <div className="flex items-center justify-between">
              <span className="block text-xs text-blue-700 dark:text-blue-300/80 uppercase tracking-wider font-medium">Final Freight Value</span>
              {quote.is_breakdown_unavailable && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30">
                  ⚠️ Incomplete
                </span>
              )}
            </div>
            <span className="block text-3xl font-bold text-slate-900 dark:text-white mt-1">
              {quote.currency} {quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="block text-xs text-slate-500 dark:text-white/40 mt-1">
              BOF ({quote.basic_ocean_freight.toLocaleString()}) + Discount ({quote.discount.toLocaleString()}) + Surcharges
            </span>
          </div>

          {/* Ocean Freight & Discount */}
          <div className="space-y-2 animate-fade-in-up stagger-3">
            <h4 className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">Ocean Freight</h4>
            <div className="bg-slate-100 dark:bg-white/5 rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-200 dark:border-white/5">
                <span className="text-sm text-slate-700 dark:text-white/80">Basic Ocean Freight</span>
                <span className="text-sm font-mono font-medium text-slate-700 dark:text-white/80">
                  {quote.currency} {quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              {quote.discount !== 0 && (
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-slate-700 dark:text-white/80">Discount / Rebate</span>
                  <span className="text-sm font-mono font-medium text-red-600 dark:text-red-400">
                    {quote.currency} {quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Freight Surcharges (Included) */}
          <div className="animate-fade-in-up stagger-4">
            <ChargeTable title="Freight Surcharges (Included in Final Value)" charges={quote.included_freight_surcharges} color="text-blue-600 dark:text-blue-400" />
          </div>

          {/* Excluded Charges */}
          <div className="animate-fade-in-up stagger-5">
            <ChargeTable title="Origin & Destination Charges (Excluded)" charges={quote.excluded_charges} color="text-yellow-600 dark:text-yellow-400" />
          </div>

          {/* Uncertain Charges */}
          <div className="animate-fade-in-up stagger-6">
            <ChargeTable title="Uncertain Charges (Excluded)" charges={quote.uncertain_charges} color="text-orange-600 dark:text-orange-400" />
          </div>
        </div>
      </div>
    </>
  );
}
