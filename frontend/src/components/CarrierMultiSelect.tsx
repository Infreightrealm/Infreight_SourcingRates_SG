"use client";
import { CARRIERS } from "@/lib/types";

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
      <label className="block text-sm font-medium text-white/80">Select Carriers</label>

      {/* All Carriers Toggle */}
      <button
        type="button"
        onClick={toggleAll}
        className={`w-full px-4 py-2.5 rounded-xl border text-sm font-semibold transition-all duration-200 ${
          allSelected
            ? "bg-gradient-to-r from-blue-600 to-purple-600 border-blue-500/50 text-white shadow-lg shadow-blue-500/20"
            : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:border-white/20"
        }`}
      >
        ⚓ All Carriers
      </button>

      {/* Individual Carriers Grid */}
      <div className="grid grid-cols-3 gap-2">
        {CARRIERS.map((carrier) => (
          <button
            key={carrier.code}
            type="button"
            onClick={() => toggleCarrier(carrier.code)}
            className={`relative px-3 py-2 rounded-lg border text-xs font-medium transition-all duration-200 ${
              isSelected(carrier.code)
                ? "border-white/30 text-white shadow-md"
                : "bg-white/5 border-white/10 text-white/50 hover:bg-white/10 hover:text-white/70"
            }`}
            style={
              isSelected(carrier.code)
                ? { backgroundColor: carrier.color + "30", borderColor: carrier.color + "60" }
                : {}
            }
          >
            <span
              className="inline-block w-2 h-2 rounded-full mr-1.5"
              style={{ backgroundColor: carrier.color }}
            />
            {carrier.name}
          </button>
        ))}
      </div>
    </div>
  );
}
