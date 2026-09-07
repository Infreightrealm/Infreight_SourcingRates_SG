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
      <div className="overflow-hidden rounded-xl border border-border bg-muted/50">
        {charges.map((ch, i) => (
          <div key={i} className="flex items-center justify-between border-b border-line px-4 py-2.5 last:border-0">
            <div className="flex-1">
              <span className="text-sm text-foreground">{ch.name}</span>
              {ch.reason && <span className="mt-0.5 block text-xs text-muted-foreground">{ch.reason}</span>}
            </div>
            <span className={`text-sm font-mono font-medium ${ch.amount < 0 ? "text-destructive-foreground" : "text-foreground"}`}>
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
      <div className="animate-blur-in fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-sm" onClick={onClose} />

      {/* Drawer */}
      <div className="animate-slide-in-spring fixed right-0 top-0 z-50 h-full w-full max-w-lg overflow-y-auto border-l border-border bg-popover text-popover-foreground shadow-card-hover">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold tracking-tight text-foreground">Quote Breakdown</h3>
              <p className="text-sm text-muted-foreground">{carrier} • {quote.service_name || "N/A"}</p>
            </div>
            <button onClick={onClose} className="btn-interactive rounded-lg border border-border bg-secondary p-2 text-muted-foreground hover:bg-accent hover:text-foreground">
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
              { label: quote.port_of_discharge ? "Port of Discharge" : "Routing", value: quote.port_of_discharge || quote.routing || "—" },
            ].map((item, i) => (
              <div key={i} className={`rounded-lg px-3 py-2 ${item.label.includes("Free Time") && quote.free_time != null ? "border border-success/25 bg-success/10" : "border border-border bg-muted/50"}`}>
                <span className={`block text-xs ${item.label.includes("Free Time") && quote.free_time != null ? "font-semibold text-success-foreground" : "text-muted-foreground"}`}>{item.label}</span>
                <span className={`block text-sm font-medium ${item.label.includes("Free Time") && quote.free_time != null ? "text-success-foreground" : "text-foreground"}`}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Breakdown Unavailable Warning Banner */}
          {quote.is_breakdown_unavailable && (
            <div className="animate-fade-in-up flex items-start gap-3 rounded-2xl border border-warning/35 bg-warning/12 p-4 text-xs text-warning-foreground">
              <span className="text-xl leading-none">⚠️</span>
              <div className="space-y-1">
                <p className="text-sm font-bold">Quote Surcharges Incomplete</p>
                <p className="leading-relaxed text-muted-foreground">
                  This quote cannot accurately provide the final freight value because the price breakdown is disabled on the carrier portal:
                </p>
                <div className="mt-1.5 rounded-lg border border-warning/25 bg-warning/10 p-2 text-[11px] font-medium italic">
                  "{quote.warning_message || 'Some selected container types are currently unavailable for this sailing. Please update the container type or select another departure date.'}"
                </div>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  * Line-item surcharges (ETS, EBS, Terminal Handling) could not be scraped. The value below reflects only the basic ocean rate.
                </p>
              </div>
            </div>
          )}

          {/* Final Freight Value */}
          <div className="animate-fade-in-up stagger-2 btn-gradient rounded-xl border border-primary/25 bg-gradient-to-r from-blue-500/15 via-violet-500/15 to-blue-500/15 px-5 py-4" style={{backgroundSize: "200% 200%"}}>
            <div className="flex items-center justify-between">
              <span className="block text-xs font-medium uppercase tracking-wider text-primary">Final Freight Value</span>
              {quote.is_breakdown_unavailable && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30">
                  ⚠️ Incomplete
                </span>
              )}
            </div>
            <span className="mt-1 block text-3xl font-bold tabular-nums text-foreground">
              {quote.currency} {quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="mt-1 block text-xs text-muted-foreground">
              BOF ({quote.basic_ocean_freight.toLocaleString()}) + Discount ({quote.discount.toLocaleString()}) + Surcharges
            </span>
          </div>

          {/* Ocean Freight & Discount */}
          <div className="space-y-2 animate-fade-in-up stagger-3">
            <h4 className="text-sm font-semibold text-success-foreground">Ocean Freight</h4>
            <div className="overflow-hidden rounded-xl border border-border bg-muted/50">
              <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
                <span className="text-sm text-foreground">Basic Ocean Freight</span>
                <span className="font-mono text-sm font-medium text-foreground">
                  {quote.currency} {quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              {quote.discount !== 0 && (
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-foreground">Discount / Rebate</span>
                  <span className="text-sm font-mono font-medium text-red-600 dark:text-red-400">
                    {quote.currency} {quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Freight Surcharges (Included) */}
          <div className="animate-fade-in-up stagger-4">
            <ChargeTable title="Freight Surcharges (Included in Final Value)" charges={quote.included_freight_surcharges} color="text-primary" />
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
