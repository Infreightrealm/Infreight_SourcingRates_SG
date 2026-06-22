/**
 * Brand color tokens for the mobile app, mirrored from the web frontend
 * (dark-first aesthetic, blue -> purple gradient). Used by StyleSheet styles.
 */

export const palette = {
  bg: '#060a14',
  bgElevated: '#0a1020',
  card: '#0e1626',
  cardHi: '#121c30',
  border: 'rgba(255,255,255,0.10)',
  borderHi: 'rgba(255,255,255,0.16)',
  inputBg: 'rgba(255,255,255,0.05)',
  white: '#ffffff',
  textSecondary: 'rgba(255,255,255,0.55)',
  textMuted: 'rgba(255,255,255,0.34)',
  blue: '#3b82f6',
  purple: '#9333ea',
  emerald: '#34d399',
  amber: '#fbbf24',
  red: '#f87171',
} as const;

/** Primary brand gradient (use with expo-linear-gradient). */
export const brandGradient = ['#3b82f6', '#9333ea'] as const;

/** Per-carrier accent colors (from frontend/src/lib/types.ts, brightened for dark bg). */
export const carrierColors: Record<string, string> = {
  MAERSK: '#3aa0e0',
  ONE: '#FF00A0',
  CMA_CGM: '#3b6fd4',
  HAPAG_LLOYD: '#FF6600',
  OOCL: '#E31837',
  GREENX: '#00A34A',
  MSC: '#A0A0A0',
};
