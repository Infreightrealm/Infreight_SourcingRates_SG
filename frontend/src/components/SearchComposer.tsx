"use client";

import { ArrowLeftRight, Eraser, Loader2, Search, TriangleAlert, Weight } from "lucide-react";
import PortAutocomplete from "./PortAutocomplete";
import { isAllCarriers, toggleAllCarriers, toggleCarrierSelection } from "./CarrierMultiSelect";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { CARRIERS, CONTAINER_TYPES, REEFER_CONTAINER_TYPES, containerLabel, isReeferType } from "@/lib/types";
import { cn } from "@/lib/utils";

export type HapagRegion = "US_CA" | "EU" | "ROW";
export type DeliveryType = "PORT" | "RAMP";

const SIZE_HINT: Record<string, string> = {
  "DRY 20": "20 ft dry",
  "DRY 40": "40 ft dry",
  "DRY 40H": "40 ft high cube",
  "REEFER 20": "20 ft reefer",
  "REEFER 40": "40 ft reefer",
};

const REGIONS: Array<{ id: HapagRegion; label: string }> = [
  { id: "US_CA", label: "US / Canada" },
  { id: "EU", label: "Europe" },
  { id: "ROW", label: "Rest of World" },
];

/** The only connector that reads the ramp / inland delivery setting today. */
const RAMP_CARRIER = "CMA_CGM";

interface SearchComposerProps {
  carriers: string[];
  onCarriersChange: (carriers: string[]) => void;
  origin: string;
  onOriginChange: (v: string) => void;
  destination: string;
  onDestinationChange: (v: string) => void;
  delivery: DeliveryType;
  onDeliveryChange: (v: DeliveryType) => void;
  weight: number;
  onWeightChange: (v: number) => void;
  /** Container types that will actually be sent (reefers dropped when not allowed). */
  selectedTypes: string[];
  onToggleType: (type: string) => void;
  reeferAllowed: boolean;
  hapagUseApi: boolean;
  onHapagUseApiChange: (v: boolean) => void;
  hapagRegion: HapagRegion;
  onHapagRegionChange: (v: HapagRegion) => void;
  isLoading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  onClear: () => void;
}

/** Small two-state segmented control. */
function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
  size = "md",
}: {
  label: string;
  value: T;
  options: Array<{ id: T; label: string }>;
  onChange: (v: T) => void;
  size?: "sm" | "md";
}) {
  return (
    <div role="radiogroup" aria-label={label} className="flex gap-0.5 rounded-lg bg-secondary p-0.5">
      {options.map((o) => {
        const on = o.id === value;
        return (
          <button
            key={o.id}
            type="button"
            role="radio"
            aria-checked={on}
            onClick={() => onChange(o.id)}
            className={cn(
              "flex-1 whitespace-nowrap rounded-md font-semibold transition-colors",
              size === "sm" ? "min-h-7 px-2 text-[11px]" : "min-h-10 px-3 text-sm",
              on ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground",
            )}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

/**
 * v2 search form: route, delivery and weight on one row, equipment chips,
 * carrier pills (Hapag-Lloyd's API / Portal choice inside its pill) and a
 * summary line beside the search button. State lives in RateSearchForm.
 */
export default function SearchComposer(p: SearchComposerProps) {
  const all = isAllCarriers(p.carriers);
  const isOn = (code: string) => all || p.carriers.includes(code);
  const carrierCount = all ? CARRIERS.length : p.carriers.length;
  const hapagOn = isOn("HAPAG_LLOYD");
  const ramp = p.delivery === "RAMP";
  const sizes = p.selectedTypes.map(containerLabel);

  const swap = () => {
    const o = p.origin;
    p.onOriginChange(p.destination);
    p.onDestinationChange(o);
  };

  return (
    <form onSubmit={p.onSubmit} className="flex flex-col gap-5">
      {/* Route, delivery, weight. Lifted so the port dropdown paints over the rows below. */}
      <div className="relative z-20 grid grid-cols-1 items-end gap-3 md:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] xl:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)_auto_11rem]">
        <PortAutocomplete label="From" value={p.origin} onChange={p.onOriginChange} placeholder="e.g. Singapore" required />
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={swap}
          aria-label="Swap origin and destination"
          className="size-11 justify-self-center"
        >
          <ArrowLeftRight className="size-4" />
        </Button>
        <PortAutocomplete
          label="To"
          value={p.destination}
          onChange={p.onDestinationChange}
          placeholder="e.g. Hamburg or Montreal [CAMTR]"
          required
        />
        <div className="min-w-0">
          <div className="mb-1.5 flex min-h-[28px] items-center">
            <Label className="mb-0">Delivery</Label>
          </div>
          <Segmented
            label="Destination delivery mode"
            value={p.delivery}
            onChange={p.onDeliveryChange}
            options={[
              { id: "PORT", label: "Port to port" },
              { id: "RAMP", label: "Ramp / inland" },
            ]}
          />
        </div>
        <div className="min-w-0">
          <div className="mb-1.5 flex min-h-[28px] items-center">
            <Label htmlFor="weight-per-container" className="mb-0">
              Weight / container
            </Label>
          </div>
          <div className="relative">
            <Weight className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="weight-per-container"
              type="number"
              min={0}
              value={p.weight}
              onChange={(e) => p.onWeightChange(parseFloat(e.target.value) || 0)}
              className="min-h-11 pl-9 pr-9 tabular-nums"
            />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">kg</span>
          </div>
        </div>
      </div>

      {p.destination.toLowerCase().includes("batam") && (
        <p className="flex items-start gap-2 rounded-lg bg-warning/12 px-3 py-2 text-xs text-warning-foreground">
          <TriangleAlert className="mt-0.5 size-3.5 shrink-0" />
          Batam is generally not accepted as a direct ocean destination by major carriers, so this search may return no quotes.
        </p>
      )}

      {/* Equipment */}
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-2 flex flex-wrap items-baseline gap-x-2 text-xs">
          <span className="font-semibold text-muted-foreground">Equipment</span>
          <span className="text-muted-foreground">Reefers are priced through the Hapag-Lloyd API only.</span>
        </legend>
        <div className="flex flex-wrap gap-2">
          {[...CONTAINER_TYPES, ...REEFER_CONTAINER_TYPES].map((ct) => {
            const disabled = isReeferType(ct) && !p.reeferAllowed;
            const on = p.selectedTypes.includes(ct);
            return (
              <button
                key={ct}
                type="button"
                aria-pressed={on}
                disabled={disabled}
                onClick={() => p.onToggleType(ct)}
                title={disabled ? "Select Hapag-Lloyd and set its rate source to API" : undefined}
                className={cn(
                  "flex min-h-13 min-w-28 flex-col items-start justify-center rounded-xl border px-3 py-1.5 text-left transition-colors",
                  on && "border-foreground bg-foreground text-background",
                  !on && !disabled && "border-input bg-card text-foreground hover:bg-accent",
                  disabled && "cursor-not-allowed border-dashed border-input bg-muted text-muted-foreground",
                )}
              >
                <span className="text-[15px] font-bold leading-tight">{containerLabel(ct)}</span>
                <span className={cn("text-xs", on ? "opacity-80" : "text-muted-foreground")}>
                  {disabled ? "Needs Hapag API" : SIZE_HINT[ct]}
                </span>
              </button>
            );
          })}
        </div>
      </fieldset>

      {/* Carriers */}
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-2 flex flex-wrap items-baseline gap-x-2 text-xs">
          <span className="font-semibold text-muted-foreground">Carriers</span>
          <span className={ramp ? "font-medium text-warning-foreground" : "text-muted-foreground"}>
            {ramp
              ? "Ramp / inland is searched by CMA CGM only today. The others quote port to port."
              : `${carrierCount} of ${CARRIERS.length} selected`}
          </span>
        </legend>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            aria-pressed={all}
            onClick={() => p.onCarriersChange(toggleAllCarriers(p.carriers))}
            className={cn(
              "min-h-11 rounded-xl border px-4 text-sm font-semibold transition-colors",
              all ? "border-foreground bg-foreground text-background" : "border-input bg-card text-foreground hover:bg-accent",
            )}
          >
            All carriers
          </button>
          {CARRIERS.map((c) => {
            const on = isOn(c.code);
            const isHapag = c.code === "HAPAG_LLOYD";
            const note = !on
              ? "Off"
              : ramp
                ? c.code === RAMP_CARRIER
                  ? "Searches ramp / inland"
                  : "Port to port only"
                : isHapag
                  ? p.hapagUseApi
                    ? "Prices API"
                    : "Portal"
                  : null;
            return (
              <div
                key={c.code}
                className={cn(
                  "flex items-center rounded-xl border transition-colors",
                  on ? "border-foreground/70 bg-card" : "border-border bg-muted opacity-75",
                )}
              >
                <button
                  type="button"
                  aria-pressed={on}
                  onClick={() => p.onCarriersChange(toggleCarrierSelection(p.carriers, c.code))}
                  className="flex min-h-11 items-center gap-2 py-1.5 pl-3 pr-3 text-left"
                >
                  <span
                    className="size-2.5 shrink-0 rounded-full ring-1 ring-foreground/15"
                    style={{ backgroundColor: on ? c.color : "var(--input)" }}
                    aria-hidden
                  />
                  <span className="flex flex-col leading-tight">
                    <span className="text-sm font-semibold text-foreground">{c.name}</span>
                    {note && (
                      <span
                        className={cn(
                          "text-[11px]",
                          ramp && on && c.code !== RAMP_CARRIER ? "font-semibold text-warning-foreground" : "text-muted-foreground",
                        )}
                      >
                        {note}
                      </span>
                    )}
                  </span>
                </button>
                {isHapag && on && (
                  <div className="pr-1.5">
                    <Segmented
                      size="sm"
                      label="Hapag-Lloyd rate source"
                      value={p.hapagUseApi ? "API" : "PORTAL"}
                      onChange={(v) => p.onHapagUseApiChange(v === "API")}
                      options={[
                        { id: "API", label: "API" },
                        { id: "PORTAL", label: "Portal" },
                      ]}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {hapagOn && !p.hapagUseApi && (
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <span className="text-xs text-muted-foreground">Hapag-Lloyd contract account region</span>
            <Segmented size="sm" label="Hapag-Lloyd contract account region" value={p.hapagRegion} onChange={p.onHapagRegionChange} options={REGIONS} />
          </div>
        )}
      </fieldset>

      {/* Summary + actions; on phones it stays pinned above the tab bar while the form is on screen */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4 max-md:sticky max-md:bottom-[calc(4rem+env(safe-area-inset-bottom))] max-md:z-20 max-md:-mx-4 max-md:-mb-4 max-md:gap-2 max-md:rounded-b-xl max-md:bg-card/95 max-md:px-4 max-md:pb-3 max-md:pt-3 max-md:backdrop-blur">
        <p className="text-sm text-muted-foreground max-md:w-full max-md:text-xs">
          {sizes.length ? sizes.join(", ") : "No equipment"} · {carrierCount} carrier{carrierCount === 1 ? "" : "s"} ·{" "}
          {ramp ? "ramp / inland" : "port to port"}
          {p.weight > 0 && ` · ${p.weight.toLocaleString("en-US")} kg`}
        </p>
        <div className="flex flex-wrap gap-2 max-md:w-full max-md:flex-nowrap">
          <Button type="button" variant="outline" size="lg" onClick={p.onClear}>
            <Eraser className="size-4" />
            Clear
          </Button>
          <Button type="submit" size="lg" disabled={p.isLoading || carrierCount === 0} className="min-w-44 font-semibold max-md:min-w-0 max-md:flex-1">
            {p.isLoading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
            {p.isLoading ? "Searching…" : `Search ${carrierCount} carrier${carrierCount === 1 ? "" : "s"}`}
          </Button>
        </div>
      </div>
    </form>
  );
}
