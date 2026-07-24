"use client";
import { useState, useEffect } from "react";
import CarrierMultiSelect from "./CarrierMultiSelect";
import PortAutocomplete from "./PortAutocomplete";
import { CONTAINER_TYPES, type RateSearchRequest } from "@/lib/types";
import { toast } from "sonner";

interface RateSearchFormProps {
  onSubmit: (request: RateSearchRequest) => void;
  isLoading: boolean;
  initialValues?: Partial<RateSearchRequest>;
}

export default function RateSearchForm({ onSubmit, isLoading, initialValues }: RateSearchFormProps) {
  const [carriers, setCarriers] = useState<string[]>(initialValues?.carriers || ["ALL"]);
  const [origin, setOrigin] = useState(initialValues?.origin || "Singapore");
  const [destination, setDestination] = useState(initialValues?.destination || "Hamburg");

  const [serviceTerm, setServiceTerm] = useState("CY/CY");
  const [containerTypes, setContainerTypes] = useState<string[]>(["DRY 40H"]);
  const [weight, setWeight] = useState(20000);
  const [searchWindow, setSearchWindow] = useState(14);
  const [hapagRegion, setHapagRegion] = useState<'US_CA' | 'EU' | 'ROW'>("ROW");

  useEffect(() => {
    if (initialValues) {
      if (initialValues.origin) setOrigin(initialValues.origin);
      if (initialValues.destination) setDestination(initialValues.destination);
      if (initialValues.container_types && initialValues.container_types.length > 0) {
        setContainerTypes(initialValues.container_types);
      } else if (initialValues.container_type) {
        setContainerTypes([initialValues.container_type]);
      }
      if (initialValues.weight_per_container_kg) setWeight(initialValues.weight_per_container_kg);
    }
  }, [initialValues]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (carriers.length === 0) return;
    if (containerTypes.length === 0) {
      toast.error("At least one container type must be selected");
      return;
    }

    if (destination.toLowerCase().includes("batam")) {
      toast.warning("Warning: Batam is generally not accepted as a direct ocean destination by carriers. The search may return no results.", {
        duration: 10000,
      });
    }

    onSubmit({
      carriers,
      origin,
      destination,
      service_term: serviceTerm,
      container_types: containerTypes,
      container_quantity: 1, // Fixed to 1
      weight_per_container_kg: weight,
      commodity: "Furniture", // Fixed to Furniture
      departure_date: "tomorrow", // Fixed to tomorrow
      search_window_days: searchWindow,
      hapag_region: carriers.includes("HAPAG_LLOYD") || carriers.includes("ALL") ? hapagRegion : undefined,
    });
  };

  const inputClass =
    "w-full px-4 py-2.5 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all focus-glow";
  const labelClass = "block text-sm font-medium text-slate-700 dark:text-white/80 mb-1.5";

  return (
    <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in-up">
      {/* Carrier Selection */}
      <CarrierMultiSelect selected={carriers} onChange={setCarriers} />

      {/* Hapag-Lloyd Regional Account Toggle */}
      {(carriers.includes("HAPAG_LLOYD") || carriers.includes("ALL")) && (
        <div className="p-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl animate-fade-in-up shadow-sm">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-white/40 mb-2">
            Hapag-Lloyd Contract Account Region
          </label>
          <div className="flex flex-col sm:flex-row gap-2 p-1 bg-slate-200/50 dark:bg-black/20 rounded-lg max-w-md">
            {[
              { id: "US_CA", label: "US / Canada" },
              { id: "EU", label: "Europe" },
              { id: "ROW", label: "Rest of World" }
            ].map((reg) => {
              const active = hapagRegion === reg.id;
              return (
                <button
                  key={reg.id}
                  type="button"
                  onClick={() => setHapagRegion(reg.id as any)}
                  className={`flex-1 py-2 px-3 min-h-[44px] flex items-center justify-center rounded-md text-xs font-medium transition-all duration-200 select-none ${
                    active 
                      ? "bg-blue-600 text-white shadow-sm" 
                      : "text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-300/30 dark:hover:bg-white/5"
                  }`}
                >
                  {reg.label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Route Row (Origin & Destination) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in-up stagger-1">
        <PortAutocomplete
          label="Origin"
          value={origin}
          onChange={setOrigin}
          placeholder="e.g. Singapore"
          required
        />
        <PortAutocomplete
          label="Destination"
          value={destination}
          onChange={setDestination}
          placeholder="e.g. Hamburg"
          required
        />
      </div>

      {destination.toLowerCase().includes("batam") && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-600 dark:text-amber-400 text-xs flex items-start gap-3 backdrop-blur-md animate-fade-in-up stagger-1 shadow-sm shadow-amber-500/5">
          <span className="text-base flex-shrink-0">⚠️</span>
          <div>
            <span className="font-semibold block mb-0.5">Destination Warning</span>
            Batam is generally not accepted as a direct ocean destination by major carriers. Searching with Batam may result in zero quotes or failed carrier connections.
          </div>
        </div>
      )}

      {/* Container Details & Weight Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 animate-fade-in-up stagger-2">
        <div className="sm:col-span-2">
          <label className={labelClass}>Container Types</label>
          <div className="flex flex-col sm:flex-row flex-wrap gap-2.5 sm:gap-3 mt-2.5">
            {CONTAINER_TYPES.map((ct) => {
              const isSelected = containerTypes.includes(ct);
              const displayName = ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct;
              return (
                <label key={ct} className="flex items-center gap-2.5 px-3.5 py-2.5 min-h-[44px] bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl cursor-pointer text-sm font-medium text-slate-700 dark:text-white/80 select-none transition-all hover:bg-slate-200 dark:hover:bg-white/10">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => {
                      if (isSelected) {
                        if (containerTypes.length > 1) {
                          setContainerTypes(containerTypes.filter(t => t !== ct));
                        } else {
                          toast.error("At least one container type must be selected");
                        }
                      } else {
                        setContainerTypes([...containerTypes, ct]);
                      }
                    }}
                    className="w-4 h-4 rounded text-blue-600 border-slate-300 dark:border-white/10 focus:ring-blue-500 bg-slate-100 dark:bg-white/5"
                  />
                  <span>{displayName}</span>
                </label>
              );
            })}
          </div>
        </div>

        <div>
          <label className={labelClass}>Weight PER CONTAINER (KG)</label>
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(parseFloat(e.target.value) || 0)}
            className={`${inputClass} min-h-[44px]`}
            min={0}
          />
        </div>
      </div>

      {/* Submit & Clear Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          type="submit"
          disabled={isLoading || carriers.length === 0}
          className="flex-1 py-3.5 px-6 min-h-[44px] rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 btn-interactive btn-gradient shine-on-hover flex items-center justify-center"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Searching…
            </span>
          ) : (
            "🔍 Search Rates"
          )}
        </button>

        <button
          type="button"
          onClick={() => {
            setOrigin("");
            setDestination("");
            setWeight(20000);
            setContainerTypes(["DRY 40H"]);
            toast.info("Cleared search fields (Origin, Destination, Weight, Container Types). RFQ text preserved.");
          }}
          className="px-4 py-3.5 min-h-[44px] rounded-xl font-medium text-xs text-slate-600 dark:text-slate-300 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 transition-all flex items-center justify-center gap-1.5"
        >
          🧹 Clear Search Fields
        </button>
      </div>


    </form>
  );
}
