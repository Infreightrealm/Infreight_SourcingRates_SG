"use client";
import { CARRIERS } from "@/lib/types";
import { Label } from "@/components/ui/input";
import { Anchor, Check } from "lucide-react";

interface CarrierMultiSelectProps {
  selected: string[];
  onChange: (carriers: string[]) => void;
}

export default function CarrierMultiSelect({ selected, onChange }: CarrierMultiSelectProps) {
  const allSelected = selected.includes("ALL") || selected.length === CARRIERS.length;

  const toggleAll = () => {
    if (allSelected) {
      onChange([]);
    } else {
      onChange(["ALL"]);
    }
  };

  const toggleCarrier = (code: string) => {
    if (selected.includes("ALL")) {
      // Switching from ALL to specific: select all except the clicked one
      onChange(CARRIERS.filter((c) => c.code !== code).map((c) => c.code));
    } else if (selected.includes(code)) {
      onChange(selected.filter((c) => c !== code));
    } else {
      const newSelected = [...selected, code];
      if (newSelected.length === CARRIERS.length) {
        onChange(["ALL"]);
      } else {
        onChange(newSelected);
      }
    }
  };

  const isSelected = (code: string) => allSelected || selected.includes(code);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <Label className="mb-0">Select Carriers</Label>
        <span className="text-xs text-muted-foreground tabular-nums">
          {allSelected ? CARRIERS.length : selected.length} of {CARRIERS.length} selected
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
          return (
            <button
              key={carrier.code}
              type="button"
              aria-pressed={active}
              onClick={() => toggleCarrier(carrier.code)}
              className={`btn-interactive animate-fade-in-up relative flex min-h-[44px] items-center justify-center gap-1.5 rounded-lg border px-3 py-2.5 text-xs font-medium ${
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
              {active && <Check className="ml-auto size-3.5 opacity-60" />}
            </button>
          );
        })}
      </div>

    </div>
  );
}
