/**
 * App-wide constants: backend base URL, carrier list, container types, and the
 * per-status badge styling map (ported from the web frontend's STATUS_MAP, with
 * Tailwind classes converted to RN-friendly hex/rgba colors).
 */
import { palette } from '@/theme/colors';

const rawApiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
export const API_URL =
  rawApiUrl.startsWith('http://') || rawApiUrl.startsWith('https://')
    ? rawApiUrl
    : `https://${rawApiUrl}`;

export const CARRIERS = [
  { code: 'MAERSK', name: 'Maersk' },
  { code: 'ONE', name: 'ONE' },
  { code: 'CMA_CGM', name: 'CMA CGM' },
  { code: 'HAPAG_LLOYD', name: 'Hapag-Lloyd' },
  { code: 'OOCL', name: 'OOCL' },
  { code: 'GREENX', name: 'GreenX' },
  { code: 'MSC', name: 'MSC' },
] as const;

/** Maps rate-search carrier codes to the noVNC carrier codes used by /api/vnc-status. */
export const VNC_CARRIER_CODE: Record<string, string> = {
  MAERSK: 'maersk',
  CMA_CGM: 'cma',
  ONE: 'one',
  HAPAG_LLOYD: 'hapag',
  GREENX: 'greenx',
  MSC: 'msc',
  OOCL: 'oocl',
};

export const CONTAINER_TYPES = [
  'DRY 20',
  'DRY 40',
  'DRY 40H',
  'REEFER 20',
  'REEFER 40',
  'REEFER 40H',
] as const;

export interface StatusStyle {
  label: string;
  color: string; // foreground (text + dot)
  bg: string; // pill background
}

export const STATUS_MAP: Record<string, StatusStyle> = {
  QUEUED: { label: 'Queued', color: palette.textMuted, bg: 'rgba(148,163,184,0.12)' },
  RUNNING: { label: 'Searching…', color: palette.blue, bg: 'rgba(59,130,246,0.14)' },
  AVAILABLE_QUOTES_FOUND: { label: 'Quotes Found', color: palette.emerald, bg: 'rgba(52,211,153,0.12)' },
  NO_QUOTES_AVAILABLE: { label: 'No Quotes', color: palette.amber, bg: 'rgba(251,191,36,0.12)' },
  COMPLETED: { label: 'Completed', color: palette.emerald, bg: 'rgba(52,211,153,0.12)' },
  PARTIAL_COMPLETED: { label: 'Partial', color: palette.amber, bg: 'rgba(251,191,36,0.12)' },
  FAILED: { label: 'Failed', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  LOGIN_FAILED: { label: 'Login Failed', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  CONNECTOR_NOT_AVAILABLE: { label: 'Not Available', color: palette.textMuted, bg: 'rgba(148,163,184,0.12)' },
  TIMEOUT: { label: 'Timeout', color: '#fb923c', bg: 'rgba(251,146,60,0.12)' },
  UNKNOWN_ERROR: { label: 'Error', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  EXTRACTION_FAILED: { label: 'Extraction Failed', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  CAPTCHA_OR_MANUAL_REVIEW_REQUIRED: { label: 'CAPTCHA Required', color: palette.amber, bg: 'rgba(251,191,36,0.12)' },
  MANUAL_ACTION_REQUIRED: { label: 'Action Required', color: palette.amber, bg: 'rgba(251,191,36,0.12)' },
  WAITING_FOR_HUMAN_VERIFICATION: { label: 'Solve CAPTCHA', color: palette.amber, bg: 'rgba(251,191,36,0.12)' },
  BOT_CHALLENGE_DETECTED: { label: 'CAPTCHA Detected', color: '#fb923c', bg: 'rgba(251,146,60,0.12)' },
  CARRIER_SITE_CHANGED: { label: 'Site Changed', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  INVALID_SEARCH_INPUT: { label: 'No Port Pairing', color: palette.red, bg: 'rgba(248,113,113,0.12)' },
  PRICE_BREAKDOWN_NOT_FOUND: { label: 'No Breakdown', color: '#fb923c', bg: 'rgba(251,146,60,0.12)' },
};

export function statusStyle(status: string): StatusStyle {
  return STATUS_MAP[status] ?? { label: status, color: palette.textMuted, bg: 'rgba(148,163,184,0.12)' };
}
