import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge conditional class names and de-duplicate conflicting Tailwind
 * utilities. Same helper the Componentry primitives are written against.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/* ─── Motion tokens ─────────────────────────────────────────────
 * Easing curves mirror the CSS custom properties in globals.css.
 * Strong custom curves — defaults like `ease-out` feel weak.
 */

export const EASE_OUT = [0.16, 1, 0.3, 1] as const;
export const EASE_IN_OUT = [0.77, 0, 0.175, 1] as const;

/** CSS string form of EASE_OUT for inline style transitions. */
export const EASE_OUT_CSS = "cubic-bezier(0.16, 1, 0.3, 1)";
