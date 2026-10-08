"use client";
import { CARRIERS } from "@/lib/types";
import { Label } from "@/components/ui/input";
import { Anchor, Check } from "lucide-react";
import { useSwitchedOffCarriers } from "@/lib/carrierSwitches";

interface CarrierMultiSelectProps {
  selected: string[];
  onChange: (carriers: string[]) => void;
}

/** True when every carrier is selected ("ALL" or each code listed). */
export function isAllCarriers(selected: string[]) {
  return selected.includes("ALL") || selected.length === CARRIERS.length;
}

/** The selection after toggling "All carriers". */
export function toggleAllCarriers(selected: string[]): string[] {
  return isAllCarriers(selected) ? [] : ["ALL"];
}

/** The selection after toggling one carrier; a full set collapses to ["ALL"]. */
export function toggleCarrierSelection(selected: string[], code: string): string[] {
  if (selected.includes("ALL")) {
    // Switching from ALL to specific: select all except the clicked one
    return CARRIERS.filter((c) => c.code !== code).map((c) => c.code);
  }
  if (selected.includes(code)) return selected.filter((c) => c !== code);
  const next = [...selected, code];
  return next.length === CARRIERS.length ? ["ALL"] : next;
}

export default function CarrierMultiSelect({ selected, onChange }: CarrierMultiSelectProps) {
  const allSelected = isAllCarriers(selected);

  const toggleAll = () => onChange(toggleAllCarriers(selected));

  const toggleCarrier = (code: string) => onChange(toggleCarrierSelection(selected, code));

  // Carriers an admin switched off (site down) can't be picked; the backend skips them too.
  const switchedOff = useSwitchedOffCarriers();
  const isSelected = (code: string) => !(code in switchedOff) && (allSelected || selected.includes(code));
  const selectedCount = CARRIERS.filter((c) => isSelected(c.code)).length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <Label className="mb-0">Select Carriers</Label>
        <span className="text-xs text-muted-foreground tabular-nums">
          {selectedCount} of {CARRIERS.length} selected
        </span>
      </div>

      {/* All Carriers Toggle */}
      <button
        type="button"
        aria-pressed={allSelected}
        onClick={toggleAll}
        className={`btn-interactive shine-on-hover flex min-h-[44px] w-full items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold ${
          allSelected
            ? "bg-gradient-brand border-transparent text-white shadow-brand"
            : "border-border bg-card text-muted-foreground hover:bg-accent hover:text-foreground"
        }`}
      >
        <Anchor className="size-4" />
        All Carriers
      </button>

      {/* Individual Carriers Grid */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3">
        {CARRIERS.map((carrier, index) => {
          const active = isSelected(carrier.code);
          const offByAdmin = carrier.code in switchedOff;
          return (
            <button
              key={carrier.code}
              type="button"
              aria-pressed={active}
              disabled={offByAdmin}
              title={offByAdmin ? `Switched off by admin${switchedOff[carrier.code] ? `: ${switchedOff[carrier.code]}` : ""}` : undefined}
              onClick={() => toggleCarrier(carrier.code)}
              className={`btn-interactive animate-fade-in-up relative flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border px-3 py-2.5 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-50 ${
                active
                  ? "text-foreground shadow-panel"
                  : "border-border bg-card text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
              style={{
                animationDelay: `${index * 0.04}s`,
                ...(active
                  ? { backgroundColor: carrier.color + "22", borderColor: carrier.color + "66" }
                  : {})
              }}
            >
              <span
                className="inline-block size-2 shrink-0 rounded-full"
                style={{
                  backgroundColor: carrier.color,
                  boxShadow: active ? `0 0 0 3px ${carrier.color}26` : undefined,
                }}
              />
              {carrier.name}
              {offByAdmin && <span className="ml-auto text-[10px] font-semibold uppercase text-destructive-foreground">Off</span>}
              {active && <Check className="ml-auto size-3.5 opacity-60" />}
            </button>
          );
        })}
      </div>

    </div>
  );
}
