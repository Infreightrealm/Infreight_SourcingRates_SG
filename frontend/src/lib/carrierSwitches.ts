"use client";

import { useEffect, useState } from "react";
import { getCarrierSwitches } from "./api";

/** How often the search form re-checks which carriers are switched off. */
const REFRESH_MS = 60_000;

/**
 * Carriers an admin has switched off (site down / maintenance), as code -> reason
 * (null when no reason was given). Refreshes every minute; empty if the check fails,
 * since the backend skips switched-off carriers anyway.
 */
export function useSwitchedOffCarriers(): Record<string, string | null> {
  const [off, setOff] = useState<Record<string, string | null>>({});

  useEffect(() => {
    let alive = true;
    const load = () =>
      getCarrierSwitches()
        .then((all) => {
          if (!alive) return;
          const next: Record<string, string | null> = {};
          for (const [code, s] of Object.entries(all)) if (!s.enabled) next[code] = s.reason;
          setOff(next);
        })
        .catch(() => {});
    void load();
    const timer = setInterval(load, REFRESH_MS);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  return off;
}
