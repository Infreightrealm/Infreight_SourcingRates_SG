"use client";
import { useState } from "react";
import CarrierMultiSelect from "./CarrierMultiSelect";
import PortAutocomplete from "./PortAutocomplete";
import { CONTAINER_TYPES, type RateSearchRequest } from "@/lib/types";
import { toast } from "sonner";

interface RateSearchFormProps {
  onSubmit: (request: RateSearchRequest) => void;
  isLoading: boolean;
}

export default function RateSearchForm({ onSubmit, isLoading }: RateSearchFormProps) {
  const [carriers, setCarriers] = useState<string[]>(["ALL"]);
  const [origin, setOrigin] = useState("SGSIN");
  const [destination, setDestination] = useState("DEHAM");
  const [serviceTerm, setServiceTerm] = useState("CY/CY");
  const [containerType, setContainerType] = useState("DRY 40H");
  const [containerQty, setContainerQty] = useState(1);
  const [weight, setWeight] = useState(20000);
  const [commodity, setCommodity] = useState("Furniture");
  const [departureDate, setDepartureDate] = useState("tomorrow");
  const [searchWindow, setSearchWindow] = useState(14);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (carriers.length === 0) return;

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
      container_type: containerType,
      container_quantity: containerQty,
      weight_per_container_kg: weight,
      commodity,
      departure_date: departureDate,
      search_window_days: searchWindow,
    });
  };

  const inputClass =
    "w-full px-4 py-2.5 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all";
  const labelClass = "block text-sm font-medium text-slate-700 dark:text-white/80 mb-1.5";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Carrier Selection */}
      <CarrierMultiSelect selected={carriers} onChange={setCarriers} />

      {/* Route Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PortAutocomplete
          label="Origin"
          value={origin}
          onChange={setOrigin}
          placeholder="e.g. SGSIN"
          required
        />
        <PortAutocomplete
          label="Destination"
          value={destination}
          onChange={setDestination}
          placeholder="e.g. DEHAM"
          required
        />
      </div>

      {destination.toLowerCase().includes("batam") && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-600 dark:text-amber-400 text-xs flex items-start gap-3 backdrop-blur-md animate-fade-in shadow-sm shadow-amber-500/5">
          <span className="text-base flex-shrink-0">⚠️</span>
          <div>
            <span className="font-semibold block mb-0.5">Destination Warning</span>
            Batam is generally not accepted as a direct ocean destination by major carriers. Searching with Batam may result in zero quotes or failed carrier connections.
          </div>
        </div>
      )}

      {/* Container Details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className={labelClass}>Service Term</label>
          <select value={serviceTerm} onChange={(e) => setServiceTerm(e.target.value)} className={inputClass}>
            <option value="CY/CY">CY/CY</option>
            <option value="CY/SD">CY/SD</option>
            <option value="SD/CY">SD/CY</option>
            <option value="SD/SD">SD/SD</option>
          </select>
        </div>
        <div>
          <label className={labelClass}>Container Type</label>
          <select value={containerType} onChange={(e) => setContainerType(e.target.value)} className={inputClass}>
            {CONTAINER_TYPES.map((ct) => (
              <option key={ct} value={ct}>{ct}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Quantity</label>
          <input type="number" value={containerQty} onChange={(e) => setContainerQty(parseInt(e.target.value) || 1)} className={inputClass} min={1} />
        </div>
        <div>
          <label className={labelClass}>Weight (KG)</label>
          <input type="number" value={weight} onChange={(e) => setWeight(parseFloat(e.target.value) || 0)} className={inputClass} min={0} />
        </div>
      </div>

      {/* Commodity & Date */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className={labelClass}>Commodity</label>
          <input type="text" value={commodity} onChange={(e) => setCommodity(e.target.value)} className={inputClass} placeholder="e.g. Furniture" required />
        </div>
        <div>
          <label className={labelClass}>Departure Date</label>
          <input
            type="text"
            value={departureDate}
            onChange={(e) => setDepartureDate(e.target.value)}
            className={inputClass}
            placeholder="tomorrow or YYYY-MM-DD"
          />
        </div>
        <div>
          <label className={labelClass}>Search Window (days)</label>
          <input type="number" value={searchWindow} onChange={(e) => setSearchWindow(parseInt(e.target.value) || 14)} className={inputClass} min={1} max={90} />
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading || carriers.length === 0}
        className="w-full py-3 px-6 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30"
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
    </form>
  );
}
