/**
 * API client types — ported from the web frontend (frontend/src/lib/types.ts)
 * to keep the mobile and web models in sync with the FastAPI backend schemas.
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
  queue_position?: number;
  active_search_info?: string;
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
  user_name?: string;
}

export interface UserSchema {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface VncCarrier {
  name: string;
  code: string;
  path: string;
  ws_path: string;
}

export interface VncStatus {
  available: boolean;
  carriers: VncCarrier[];
  vnc_path: string;
  message: string;
}

export interface PortSuggestion {
  name: string;
  code?: string;
  country?: string;
  country_name?: string;
  status?: string;
  [key: string]: unknown;
}

/** Terminal search statuses that stop the results poller. */
export const TERMINAL_STATUSES = ['COMPLETED', 'PARTIAL_COMPLETED', 'FAILED'] as const;
