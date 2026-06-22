/** Quote helpers shared by the results screen and QuoteCard. */
import type { CarrierResultSchema, QuoteSchema } from '@/types/api';

/** Lowest priced quote (final freight value > 0) for a carrier, or null. */
export function bestQuote(quotes: QuoteSchema[]): QuoteSchema | null {
  return quotes.reduce<QuoteSchema | null>((best, q) => {
    if (!(q.final_freight_value > 0)) return best;
    if (!best || q.final_freight_value < best.final_freight_value) return q;
    return best;
  }, null);
}

export function money(value: number, currency = 'USD'): string {
  const prefix = currency === 'USD' ? '$' : `${currency} `;
  return `${prefix}${Math.round(value).toLocaleString('en-US')}`;
}

const ACTIVE_STATUSES = new Set(['QUEUED', 'RUNNING']);

/**
 * Sort carrier results for display: priced carriers first (cheapest first),
 * then still-running carriers, then everything else (errors / no quotes).
 */
export function sortResults(results: CarrierResultSchema[]): CarrierResultSchema[] {
  return [...results].sort((a, b) => {
    const pa = bestQuote(a.quotes)?.final_freight_value ?? null;
    const pb = bestQuote(b.quotes)?.final_freight_value ?? null;
    if (pa !== null && pb !== null) return pa - pb;
    if (pa !== null) return -1;
    if (pb !== null) return 1;
    const aActive = ACTIVE_STATUSES.has(a.status);
    const bActive = ACTIVE_STATUSES.has(b.status);
    if (aActive !== bActive) return aActive ? -1 : 1;
    return 0;
  });
}

/** The single cheapest result across all carriers, if any are priced. */
export function cheapestResult(
  results: CarrierResultSchema[],
): { carrier: string; value: number; currency: string } | null {
  let best: { carrier: string; value: number; currency: string } | null = null;
  for (const r of results) {
    const q = bestQuote(r.quotes);
    if (q && (!best || q.final_freight_value < best.value)) {
      best = { carrier: r.carrier, value: q.final_freight_value, currency: q.currency };
    }
  }
  return best;
}
