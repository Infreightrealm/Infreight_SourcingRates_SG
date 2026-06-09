/**
 * API client types matching the backend schemas.
 */

export interface ChargeSchema {
  name: string;
  amount: number;
  currency: string;
  category?: string;
  reason?: string;
}

export interface QuoteSchema {
  etd?: string;
  eta?: string;
  transit_time_days?: number;
  routing?: string;
  free_time?: number;
  service_name?: string;
  vessel?: string;
  container_type?: string;
  container_quantity?: number;
  currency: string;
  basic_ocean_freight: number;
  discount: number;
  included_freight_surcharges: ChargeSchema[];
  excluded_charges: ChargeSchema[];
  uncertain_charges: ChargeSchema[];
  final_freight_value: number;
  source: string;
  raw_reference?: string;
}

export interface CarrierResultSchema {
  carrier: string;
  status: string;
  error_message?: string;
  quotes: QuoteSchema[];
}

export interface RateSearchCreateResponse {
  search_id: string;
  status: string;
}

export interface RateSearchResultResponse {
  search_id: string;
  status: string;
  origin?: string;
  destination?: string;
  container_type?: string;
  container_quantity?: number;
  commodity?: string;
  created_at?: string;
  results: CarrierResultSchema[];
}

export interface RateSearchRequest {
  carriers: string[];
  origin: string;
  destination: string;
  service_term: string;
  container_type: string;
  container_quantity: number;
  weight_per_container_kg: number;
  commodity: string;
  departure_date: string;
  search_window_days: number;
}

export const CARRIERS = [
  { code: "MAERSK", name: "Maersk", color: "#004B8D" },
  { code: "ONE", name: "ONE", color: "#FF00A0" },
  { code: "CMA_CGM", name: "CMA CGM", color: "#002B5C" },
  { code: "HAPAG_LLOYD", name: "Hapag-Lloyd", color: "#FF6600" },
  { code: "OOCL", name: "OOCL", color: "#E31837" },
] as const;

export const CONTAINER_TYPES = [
  "DRY 20",
  "DRY 40",
  "DRY 40H",
  "REEFER 20",
  "REEFER 40",
  "REEFER 40H",
] as const;

export const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  QUEUED: { label: "Queued", color: "text-gray-400", bg: "bg-gray-400/10" },
  RUNNING: { label: "Searching…", color: "text-blue-400", bg: "bg-blue-400/10" },
  AVAILABLE_QUOTES_FOUND: { label: "Quotes Found", color: "text-emerald-400", bg: "bg-emerald-400/10" },
  NO_QUOTES_AVAILABLE: { label: "No Quotes", color: "text-yellow-400", bg: "bg-yellow-400/10" },
  COMPLETED: { label: "Completed", color: "text-emerald-400", bg: "bg-emerald-400/10" },
  PARTIAL_COMPLETED: { label: "Partial", color: "text-amber-400", bg: "bg-amber-400/10" },
  FAILED: { label: "Failed", color: "text-red-400", bg: "bg-red-400/10" },
  LOGIN_FAILED: { label: "Login Failed", color: "text-red-400", bg: "bg-red-400/10" },
  CONNECTOR_NOT_AVAILABLE: { label: "Not Available", color: "text-gray-500", bg: "bg-gray-500/10" },
  TIMEOUT: { label: "Timeout", color: "text-orange-400", bg: "bg-orange-400/10" },
  UNKNOWN_ERROR: { label: "Error", color: "text-red-400", bg: "bg-red-400/10" },
  EXTRACTION_FAILED: { label: "Extraction Failed", color: "text-red-400", bg: "bg-red-400/10" },
  CAPTCHA_OR_MANUAL_REVIEW_REQUIRED: { label: "CAPTCHA Required", color: "text-orange-400", bg: "bg-orange-400/10" },
  CARRIER_SITE_CHANGED: { label: "Site Changed", color: "text-red-400", bg: "bg-red-400/10" },
  INVALID_SEARCH_INPUT: { label: "No Port Pairing", color: "text-red-400", bg: "bg-red-400/10" },
  PRICE_BREAKDOWN_NOT_FOUND: { label: "No Breakdown", color: "text-orange-400", bg: "bg-orange-400/10" },
};
