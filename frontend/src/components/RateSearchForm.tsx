"use client";
import { useState, useEffect } from "react";
import CarrierMultiSelect from "./CarrierMultiSelect";
import PortAutocomplete from "./PortAutocomplete";
import { CONTAINER_TYPES, type RateSearchRequest } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { ShimmerButton } from "@/components/ui/shimmer-button";
import { cn } from "@/lib/utils";
import {
  Anchor,
  Container,
  Eraser,
  Loader2,
  Search,
  TrainTrack,
  TriangleAlert,
  Weight,
} from "lucide-react";
import { toast } from "sonner";

interface RateSearchFormProps {
  onSubmit: (request: RateSearchRequest) => void;
  isLoading: boolean;
  initialValues?: Partial<RateSearchRequest>;
  selectedCarriers?: string[];
  onCarrierChange?: (carriers: string[]) => void;
  /** Reports the route as it is edited, so it can be pinned before searching. */
  onRouteChange?: (route: {
    origin: string;
    destination: string;
    containerTypes: string[];
    weightKg: number;
    destinationDeliveryType?: 'PORT' | 'RAMP';
  }) => void;
}

export default function RateSearchForm({ onSubmit, isLoading, initialValues, selectedCarriers, onCarrierChange, onRouteChange }: RateSearchFormProps) {
  const [carriers, setCarriers] = useState<string[]>(selectedCarriers || initialValues?.carriers || ["ALL"]);

  const handleCarrierChange = (newCarriers: string[]) => {
    setCarriers(newCarriers);
    if (onCarrierChange) onCarrierChange(newCarriers);
  };
  const [origin, setOrigin] = useState(initialValues?.origin || "Singapore");
  const [destination, setDestination] = useState(initialValues?.destination || "Hamburg");
  const [destinationDeliveryType, setDestinationDeliveryType] = useState<'PORT' | 'RAMP'>(
    initialValues?.destination_delivery_type || (initialValues?.prefer_ramp ? 'RAMP' : 'PORT')
  );

  const [serviceTerm, setServiceTerm] = useState("CY/CY");
  const [containerTypes, setContainerTypes] = useState<string[]>(["DRY 40H"]);
  const [weight, setWeight] = useState(20000);
  const [searchWindow, setSearchWindow] = useState(14);
  const [hapagRegion, setHapagRegion] = useState<'US_CA' | 'EU' | 'ROW'>("ROW");
  const [hapagUseApi, setHapagUseApi] = useState(false);

  useEffect(() => {
    if (initialValues) {
      if (initialValues.origin) setOrigin(initialValues.origin);
      if (initialValues.destination) setDestination(initialValues.destination);
      if (initialValues.destination_delivery_type) {
        setDestinationDeliveryType(initialValues.destination_delivery_type);
      } else if (initialValues.prefer_ramp !== undefined) {
        setDestinationDeliveryType(initialValues.prefer_ramp ? "RAMP" : "PORT");
      }
      if (initialValues.container_types && initialValues.container_types.length > 0) {
        setContainerTypes(initialValues.container_types);
      } else if (initialValues.container_type) {
        setContainerTypes([initialValues.container_type]);
      }
      if (initialValues.weight_per_container_kg) setWeight(initialValues.weight_per_container_kg);
    }
  }, [initialValues]);

  // Mirror the route upward so the workspace panel can pin it without
  // waiting for a search to run.
  useEffect(() => {
    onRouteChange?.({ origin, destination, containerTypes, weightKg: weight, destinationDeliveryType });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [origin, destination, containerTypes, weight, destinationDeliveryType]);

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
      service_term: destinationDeliveryType === "RAMP" ? "CY/RAMP" : serviceTerm,
      destination_delivery_type: destinationDeliveryType,
      prefer_ramp: destinationDeliveryType === "RAMP",
      container_types: containerTypes,
      container_quantity: 1, // Fixed to 1
      weight_per_container_kg: weight,
      commodity: "Furniture", // Fixed to Furniture
      departure_date: "tomorrow", // Fixed to tomorrow
      search_window_days: searchWindow,
      hapag_region: carriers.includes("HAPAG_LLOYD") || carriers.includes("ALL") ? hapagRegion : undefined,
      hapag_use_api: carriers.includes("HAPAG_LLOYD") || carriers.includes("ALL") ? hapagUseApi : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in-up">
      {/* Carrier Selection */}
      <CarrierMultiSelect selected={carriers} onChange={handleCarrierChange} />

      {/* Hapag-Lloyd Regional Account Toggle */}
      {(carriers.includes("HAPAG_LLOYD") || carriers.includes("ALL")) && (
        <Card variant="subtle" className="animate-fade-in-up rounded-xl p-4">
          {/* Rate source: portal scraping (default) or the Hapag-Lloyd Prices API */}
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <Label className="mr-1">Hapag-Lloyd Rate Source</Label>
            <span className={`text-xs font-medium ${hapagUseApi ? "text-muted-foreground" : "text-foreground"}`}>
              Portal scraping
            </span>
            <button
              type="button"
              role="switch"
              aria-checked={hapagUseApi}
              aria-label="Use Hapag-Lloyd Prices API instead of portal scraping"
              onClick={() => setHapagUseApi((v) => !v)}
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border border-border transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                hapagUseApi ? "bg-primary" : "bg-muted"
              }`}
            >
              <span
                className={`inline-block size-4 rounded-full bg-background shadow-panel transition-transform duration-200 ${
                  hapagUseApi ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
            <span className={`text-xs font-medium ${hapagUseApi ? "text-foreground" : "text-muted-foreground"}`}>
              Prices API
            </span>
            {hapagUseApi && (
              <span className="basis-full text-xs text-muted-foreground">
                Quick Quotes + Spot from the official API. Each container type uses one API call.
              </span>
            )}
          </div>

          {!hapagUseApi && (<>
          <Label className="mb-2">Hapag-Lloyd Contract Account Region</Label>
          <div
            role="radiogroup"
            aria-label="Hapag-Lloyd contract account region"
            className="flex max-w-md flex-col gap-1 rounded-lg border border-border bg-background/60 p-1 sm:flex-row"
          >
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
                  role="radio"
                  aria-checked={active}
                  onClick={() => setHapagRegion(reg.id as any)}
                  className={`flex min-h-[40px] flex-1 select-none items-center justify-center rounded-md px-3 py-2 text-xs font-medium transition-all duration-200 ${
                    active
                      ? "bg-primary text-primary-foreground shadow-panel"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  {reg.label}
                </button>
              );
            })}
          </div>
          </>)}
        </Card>
      )}

      {/* Route Row (Origin & Destination) — lifted above the rows below it so
          the port autocomplete dropdown isn't painted behind them. */}
      <div className="relative z-20 grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fade-in-up stagger-1">
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
          placeholder="e.g. Hamburg or Montreal [CAMTR]"
          required
          icon={destinationDeliveryType === "RAMP" ? TrainTrack : Anchor}
          headerRight={
            <div
              role="radiogroup"
              aria-label="Destination delivery mode"
              className="relative inline-flex items-center rounded-lg border border-border/80 bg-muted/60 dark:bg-muted/30 p-0.5 shadow-2xs backdrop-blur-xs select-none"
            >
              {/* Sliding highlight pill */}
              <span
                aria-hidden="true"
                className={cn(
                  "absolute top-0.5 bottom-0.5 w-[calc(50%-2px)] rounded-md bg-background dark:bg-card shadow-xs transition-all duration-200 ease-out border border-border/50",
                  destinationDeliveryType === "PORT"
                    ? "left-0.5"
                    : "left-[calc(50%+1px)]"
                )}
              />

              <button
                type="button"
                role="radio"
                aria-checked={destinationDeliveryType === "PORT"}
                onClick={() => setDestinationDeliveryType("PORT")}
                className={cn(
                  "relative z-10 flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-medium rounded-md transition-colors select-none cursor-pointer",
                  destinationDeliveryType === "PORT"
                    ? "text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                )}
                title="Deliver to ocean port / container terminal"
              >
                <Anchor className="size-3 shrink-0" />
                <span>Port</span>
              </button>

              <button
                type="button"
                role="radio"
                aria-checked={destinationDeliveryType === "RAMP"}
                onClick={() => setDestinationDeliveryType("RAMP")}
                className={cn(
                  "relative z-10 flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-medium rounded-md transition-colors select-none cursor-pointer",
                  destinationDeliveryType === "RAMP"
                    ? "text-primary font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                )}
                title="Deliver to inland rail ramp / container depot (e.g. Montreal CAMTR, Chicago)"
              >
                <TrainTrack className="size-3 shrink-0" />
                <span>Ramp</span>
              </button>
            </div>
          }
          helperText={
            destinationDeliveryType === "RAMP" ? (
              <div className="flex items-center gap-1.5 text-[11px] font-medium text-primary">
                <TrainTrack className="size-3 shrink-0" />
                <span>Inland Ramp delivery active — routes to rail ramp / container depot (e.g. CAMTR, USCHI).</span>
              </div>
            ) : null
          }
        />
      </div>

      {destination.toLowerCase().includes("batam") && (
        <Card variant="warning" className="animate-fade-in-up stagger-1 flex items-start gap-3 rounded-xl p-4 text-xs text-warning-foreground">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <span className="mb-0.5 block font-semibold">Destination Warning</span>
            Batam is generally not accepted as a direct ocean destination by major carriers. Searching with Batam may result in zero quotes or failed carrier connections.
          </div>
        </Card>
      )}

      {/* Container Details & Weight Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 animate-fade-in-up stagger-2">
        <div className="sm:col-span-2">
          <Label>Container Types</Label>
          <div className="mt-2.5 flex flex-col flex-wrap gap-2.5 sm:flex-row sm:gap-3">
            {CONTAINER_TYPES.map((ct) => {
              const isSelected = containerTypes.includes(ct);
              const displayName = ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct;
              return (
                <label
                  key={ct}
                  className={`btn-interactive flex min-h-[44px] cursor-pointer select-none items-center gap-2.5 rounded-xl border px-3.5 py-2.5 text-sm font-medium ${
                    isSelected
                      ? "border-primary/40 bg-primary/10 text-primary"
                      : "border-border bg-card text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
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
                    className="size-4 rounded border-input accent-[var(--primary)] focus-visible:ring-2 focus-visible:ring-ring/40"
                  />
                  <Container className="size-4 opacity-70" />
                  <span>{displayName}</span>
                </label>
              );
            })}
          </div>
        </div>

        <div>
          <Label htmlFor="weight-per-container">Weight per container (kg)</Label>
          <div className="relative">
            <Weight className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="weight-per-container"
              type="number"
              value={weight}
              onChange={(e) => setWeight(parseFloat(e.target.value) || 0)}
              className="min-h-[44px] pl-10 font-mono tabular-nums"
              min={0}
            />
          </div>
        </div>
      </div>

      {/* Submit & Clear Buttons */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <ShimmerButton
          type="submit"
          disabled={isLoading || carriers.length === 0}
          className="min-h-[48px] flex-1 text-sm"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="size-4 animate-spin" />
              Searching…
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <Search className="size-4" />
              Search Rates
            </span>
          )}
        </ShimmerButton>

        <button
          type="button"
          onClick={() => {
            setOrigin("");
            setDestination("");
            setDestinationDeliveryType("PORT");
            setWeight(20000);
            setContainerTypes(["DRY 40H"]);
            toast.info("Cleared search fields (Origin, Destination, Delivery Mode, Weight, Container Types). RFQ text preserved.");
          }}
          className="btn-interactive flex min-h-[48px] items-center justify-center gap-1.5 rounded-xl border border-border bg-secondary px-4 text-xs font-medium text-secondary-foreground hover:bg-accent"
        >
          <Eraser className="size-3.5" />
          Clear Search Fields
        </button>
      </div>


    </form>
  );
}
