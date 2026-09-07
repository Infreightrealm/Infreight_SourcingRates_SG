"use client";

import { useCallback, useSyncExternalStore } from "react";

/**
 * Per-browser workspace preferences.
 *
 * Everything here is client-only — it never reaches the backend and never
 * changes a search payload. Saved lanes are just pre-fill values for the
 * existing search form.
 */

export type AccentId = "marine" | "harbour" | "violet" | "sunset" | "graphite";
export type Density = "comfortable" | "compact";

export interface SavedLane {
  id: string;
  origin: string;
  destination: string;
  containerTypes: string[];
  weightKg: number;
}

export interface PanelVisibility {
  /** The "Quote from an email" AI RFQ reader. */
  rfq: boolean;
  /** The floating live-browser (VNC) viewer. */
  liveViewer: boolean;
  /** The floating AI assistant launcher. */
  assistant: boolean;
}

export interface Preferences {
  version: number;
  accent: AccentId;
  density: Density;
  panels: PanelVisibility;
  lanes: SavedLane[];
  /** Set once the launch intro has played; gates it to first visit. */
  introSeen: boolean;
}

export const ACCENTS: Array<{ id: AccentId; label: string; swatch: string }> = [
  { id: "marine", label: "Marine", swatch: "#2563eb" },
  { id: "harbour", label: "Harbour", swatch: "#0d9488" },
  { id: "violet", label: "Violet", swatch: "#7c3aed" },
  { id: "sunset", label: "Sunset", swatch: "#ea580c" },
  { id: "graphite", label: "Graphite", swatch: "#475569" },
];

const STORAGE_KEY = "infreight.workspace.v1";

export const DEFAULT_PREFERENCES: Preferences = {
  version: 1,
  accent: "marine",
  density: "comfortable",
  panels: { rfq: true, liveViewer: true, assistant: true },
  lanes: [],
  introSeen: false,
};

/* ─────────────────────────── Store ─────────────────────────── */

let current: Preferences = DEFAULT_PREFERENCES;
let hydrated = false;
const listeners = new Set<() => void>();

function isAccent(v: unknown): v is AccentId {
  return ACCENTS.some((a) => a.id === v);
}

/** Merge stored JSON over the defaults, dropping anything malformed. */
function coerce(raw: unknown): Preferences {
  if (!raw || typeof raw !== "object") return DEFAULT_PREFERENCES;
  const r = raw as Partial<Preferences>;
  const panels = (r.panels ?? {}) as Partial<PanelVisibility>;

  return {
    version: DEFAULT_PREFERENCES.version,
    accent: isAccent(r.accent) ? r.accent : DEFAULT_PREFERENCES.accent,
    density: r.density === "compact" ? "compact" : "comfortable",
    panels: {
      rfq: panels.rfq !== false,
      liveViewer: panels.liveViewer !== false,
      assistant: panels.assistant !== false,
    },
    lanes: Array.isArray(r.lanes)
      ? r.lanes
          .filter(
            (l): l is SavedLane =>
              !!l && typeof l.origin === "string" && typeof l.destination === "string",
          )
          .slice(0, 24)
          .map((l) => ({
            id: typeof l.id === "string" ? l.id : `${l.origin}>${l.destination}`,
            origin: l.origin,
            destination: l.destination,
            containerTypes:
              Array.isArray(l.containerTypes) && l.containerTypes.length
                ? l.containerTypes
                : ["DRY 40H"],
            weightKg: typeof l.weightKg === "number" ? l.weightKg : 20000,
          }))
      : [],
    introSeen: r.introSeen === true,
  };
}

function read(): Preferences {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? coerce(JSON.parse(raw)) : DEFAULT_PREFERENCES;
  } catch {
    // Private mode, blocked site data, corrupt JSON — defaults are fine.
    return DEFAULT_PREFERENCES;
  }
}

function emit() {
  listeners.forEach((l) => l());
}

function subscribe(listener: () => void) {
  // Hydrate lazily on first subscription so the server snapshot stays stable.
  if (!hydrated && typeof window !== "undefined") {
    hydrated = true;
    current = read();
  }
  listeners.add(listener);

  const onStorage = (e: StorageEvent) => {
    if (e.key !== STORAGE_KEY) return;
    current = read();
    emit();
  };
  window.addEventListener("storage", onStorage);

  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", onStorage);
  };
}

function getSnapshot(): Preferences {
  if (!hydrated && typeof window !== "undefined") {
    hydrated = true;
    current = read();
  }
  return current;
}

/** Stable across renders so the server and first client pass agree. */
function getServerSnapshot(): Preferences {
  return DEFAULT_PREFERENCES;
}

export function setPreferences(patch: Partial<Preferences>) {
  current = coerce({ ...current, ...patch });
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  } catch {
    // Storage unavailable — keep the in-memory value for this session.
  }
  emit();
}

export function resetPreferences() {
  const introSeen = current.introSeen;
  current = { ...DEFAULT_PREFERENCES, introSeen };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  } catch {
    /* ignore */
  }
  emit();
}

/* ─────────────────────────── Hook ─────────────────────────── */

export function usePreferences() {
  const prefs = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const setPanel = useCallback((key: keyof PanelVisibility, value: boolean) => {
    setPreferences({ panels: { ...current.panels, [key]: value } });
  }, []);

  const addLane = useCallback((lane: Omit<SavedLane, "id">) => {
    const id = `${lane.origin}>${lane.destination}>${lane.containerTypes.join("+")}`;
    if (current.lanes.some((l) => l.id === id)) return false;
    setPreferences({ lanes: [{ ...lane, id }, ...current.lanes].slice(0, 24) });
    return true;
  }, []);

  const removeLane = useCallback((id: string) => {
    setPreferences({ lanes: current.lanes.filter((l) => l.id !== id) });
  }, []);

  return { prefs, setPreferences, setPanel, addLane, removeLane, resetPreferences };
}

/** Short display label for a lane — "SGSIN → NLRTM" where LOCODEs are known. */
export function laneLabel(value: string): string {
  const locode = value.match(/\[([A-Z]{5})\]/);
  if (locode) return locode[1];
  return value.split(",")[0].trim() || value;
}
