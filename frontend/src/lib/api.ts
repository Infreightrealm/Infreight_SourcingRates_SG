/**
 * API client for the Infreight Rate Automation backend.
 */
import type { RateSearchRequest, RateSearchCreateResponse, RateSearchResultResponse, RFQParseResult } from "./types";


const defaultHeaders = {
  "ngrok-skip-browser-warning": "true"
};

// Format URL helper
function formatUrl(url: string): string {
  if (!url) return "";
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    return `https://${url}`;
  }
  return url;
}

const defaultPrimaryApiUrl = formatUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
const backupApiUrl = formatUrl(process.env.NEXT_PUBLIC_API_URL_BACKUP || "");

export function getPrimaryApiUrl(): string {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("custom_primary_api_url");
    if (saved) return formatUrl(saved);
  }
  return defaultPrimaryApiUrl;
}

export function setCustomPrimaryApiUrl(url: string) {
  if (typeof window !== "undefined") {
    if (url.trim()) {
      localStorage.setItem("custom_primary_api_url", formatUrl(url.trim()));
    } else {
      localStorage.removeItem("custom_primary_api_url");
    }
  }
}

export let API_URL = getPrimaryApiUrl();

let currentActiveUrl = getPrimaryApiUrl();
type UrlSwitchCallback = (url: string, isRestored?: boolean, reason?: string) => void;
let onUrlSwitchCallback: UrlSwitchCallback | null = null;

export function getApiUrl(): string {
  return currentActiveUrl;
}

export function registerUrlSwitchCallback(cb: UrlSwitchCallback) {
  onUrlSwitchCallback = cb;
}

let lastPrimaryCheckTime = 0;
const PRIMARY_CHECK_INTERVAL_MS = 5000; // Check primary at most once every 5s when on backup

async function probePrimaryHealth(targetUrl: string = getPrimaryApiUrl()): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(`${targetUrl}/health`, {
      headers: defaultHeaders,
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) return false;
    const data = await res.json();
    return Boolean(data && (data.status === "healthy" || data.mock_mode !== undefined));
  } catch {
    return false;
  }
}

export async function tryRestorePrimaryIfNeeded(): Promise<boolean> {
  const targetPrimary = getPrimaryApiUrl();
  if (currentActiveUrl === targetPrimary) return true;

  const now = Date.now();
  if (now - lastPrimaryCheckTime < PRIMARY_CHECK_INTERVAL_MS) {
    return false;
  }
  lastPrimaryCheckTime = now;

  const isPrimaryAlive = await probePrimaryHealth(targetPrimary);
  if (isPrimaryAlive) {
    console.info(`[API] Primary Backend ${targetPrimary} is BACK ONLINE! Restoring connection from backup.`);
    currentActiveUrl = targetPrimary;
    API_URL = targetPrimary;
    if (onUrlSwitchCallback) {
      try {
        onUrlSwitchCallback(targetPrimary, true);
      } catch (cbErr) {
        console.error("Error in URL switch callback:", cbErr);
      }
    }
    return true;
  }
  return false;
}

export async function forceRestorePrimary(): Promise<{ success: boolean; url: string; error?: string }> {
  const targetPrimary = getPrimaryApiUrl();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${targetPrimary}/health`, {
      headers: defaultHeaders,
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (res.ok) {
      const data = await res.json();
      if (data && (data.status === "healthy" || data.mock_mode !== undefined)) {
        currentActiveUrl = targetPrimary;
        API_URL = targetPrimary;
        if (onUrlSwitchCallback) {
          try {
            onUrlSwitchCallback(targetPrimary, true);
          } catch (cbErr) {
            console.error("Error in URL switch callback:", cbErr);
          }
        }
        return { success: true, url: targetPrimary };
      }
    }

    const ngrokErr = res.headers.get("Ngrok-Error-Code");
    const bodyText = await res.text().catch(() => "");
    if (ngrokErr === "ERR_NGROK_725" || bodyText.includes("ERR_NGROK_725") || bodyText.includes("bandwidth limit")) {
      return {
        success: false,
        url: targetPrimary,
        error: "ngrok account reached monthly bandwidth limit (ERR_NGROK_725). Use localtunnel ('npx localtunnel --port 8000') or run frontend locally (http://localhost:3000)."
      };
    } else if (ngrokErr) {
      return {
        success: false,
        url: targetPrimary,
        error: `ngrok returned error ${ngrokErr}. Tunnel may be closed or offline.`
      };
    }
  } catch (err: any) {
    let extraReason = "";
    if (typeof window !== "undefined" && window.location.protocol === "https:" && targetPrimary.startsWith("http://")) {
      extraReason = "Browsers block http:// (unencrypted) requests from https:// websites (Mixed Content). Use a localtunnel/ngrok https:// URL or run frontend locally (http://localhost:3000).";
    }
    return { success: false, url: targetPrimary, error: extraReason || ("Backend on " + targetPrimary + " is not responding (" + (err.message || err) + ")") };
  }

  return { success: false, url: targetPrimary, error: "Backend on " + targetPrimary + " returned invalid response." };
}

// Background auto-recovery check when running in the browser
if (typeof window !== "undefined") {
  setInterval(() => {
    if (currentActiveUrl !== getPrimaryApiUrl()) {
      tryRestorePrimaryIfNeeded();
    }
  }, 8000);
}

// Custom fetch wrapper with automatic failover and failback recovery
async function failoverFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  // If currently using backup, check if primary local backend has come back online!
  if (currentActiveUrl !== getPrimaryApiUrl()) {
    await tryRestorePrimaryIfNeeded();
  }

  const doSwitchToBackup = (reason: string): boolean => {
    if (backupApiUrl && currentActiveUrl !== backupApiUrl) {
      console.warn(`[API] Primary URL ${currentActiveUrl} failed (${reason}). Switching to backup: ${backupApiUrl}`);
      currentActiveUrl = backupApiUrl;
      API_URL = backupApiUrl;
      if (onUrlSwitchCallback) {
        try {
          onUrlSwitchCallback(backupApiUrl, false, reason);
        } catch (cbErr) {
          console.error("Error in URL switch callback:", cbErr);
        }
      }
      return true;
    }
    return false;
  };

  try {
    const res = await fetch(`${currentActiveUrl}${path}`, { ...options, headers });
    if (!res.ok && res.status >= 500 && currentActiveUrl !== backupApiUrl) {
      const switched = doSwitchToBackup(`HTTP ${res.status} Server Error`);
      if (switched) {
        try {
          return await fetch(`${currentActiveUrl}${path}`, { ...options, headers });
        } catch (backupErr) {
          console.error(`[API] Backup URL ${backupApiUrl} also failed: ${backupErr}`);
        }
      }
    }
    return res;
  } catch (primaryErr) {
    const switched = doSwitchToBackup(String(primaryErr));
    if (switched) {
      try {
        return await fetch(`${currentActiveUrl}${path}`, { ...options, headers });
      } catch (backupErr) {
        console.error(`[API] Backup URL ${backupApiUrl} also failed: ${backupErr}`);
        throw backupErr;
      }
    }
    throw primaryErr;
  }
}


export async function createRateSearch(request: RateSearchRequest): Promise<RateSearchCreateResponse> {
  const res = await failoverFetch(`/api/rate-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export async function getRateSearchResults(searchId: string): Promise<RateSearchResultResponse> {
  const res = await failoverFetch(`/api/rate-search/${searchId}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export async function releaseRateSearch(searchId: string): Promise<any> {
  const res = await failoverFetch(`/api/rate-search/${searchId}/release`, {
    method: "POST"
  });
  if (!res.ok) return null;
  return res.json().catch(() => ({}));
}

export async function pollRateSearch(
  searchId: string,
  onUpdate: (data: RateSearchResultResponse) => void,
  intervalMs = 2000,
  maxAttempts = 450, // 15 minutes
): Promise<RateSearchResultResponse> {
  let attempts = 0;
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      attempts++;
      try {
        const data = await getRateSearchResults(searchId);
        onUpdate(data);

        const runningStatuses = ["QUEUED", "RUNNING", "WAITING_FOR_HUMAN_VERIFICATION", "MANUAL_ACTION_REQUIRED"];
        const hasActiveCarrier = (data.results || []).some((r: any) =>
          runningStatuses.includes(r.status) || (r.status && r.status.startsWith("RUNNING"))
        );

        // Only stop polling when search is terminal AND no carrier is actively running.
        // For FAILED/PARTIAL_COMPLETED, ensure a minimum grace period (10 attempts = 20s) to catch late-committing quotes.
        const isTerminalStatus = ["COMPLETED", "PARTIAL_COMPLETED", "FAILED"].includes(data.status);
        const isFailureStatus = ["PARTIAL_COMPLETED", "FAILED"].includes(data.status);
        
        const shouldStop =
          (isTerminalStatus && !hasActiveCarrier && (!isFailureStatus || attempts >= 10)) ||
          attempts >= maxAttempts;

        if (shouldStop) {
          clearInterval(timer);
          resolve(data);
        }
      } catch (err) {
        if (attempts >= maxAttempts) {
          clearInterval(timer);
          reject(err);
        }
      }
    }, intervalMs);
  });
}

export async function healthCheck(): Promise<{ status: string; mock_mode: boolean }> {
  const res = await failoverFetch(`/health`);
  return res.json();
}

export async function getPortSuggestions(query: string, limit = 5): Promise<any[]> {
  if (!query || query.length < 2) return [];
  const res = await failoverFetch(`/api/ports/suggest?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function forceStopSearches(): Promise<{status: string, message: string}> {
  const res = await failoverFetch(`/api/force-stop`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to force stop searches");
  return res.json();
}

export async function getCountriesMap(): Promise<Record<string, string>> {
  const res = await failoverFetch(`/api/ports/countries`);
  if (!res.ok) return {};
  return res.json();
}

export async function getPortsConfig(adminPassword?: string): Promise<{ popular_ports: string[]; boosted_countries: string[] }> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/config/ports`, { headers });
  if (!res.ok) {
    throw new Error(`Failed to load ports config: ${res.status}`);
  }
  return res.json();
}

export async function savePortsConfig(
  config: { popular_ports: string[]; boosted_countries: string[] },
  adminPassword?: string
): Promise<{ status: string }> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/config/ports`, {
    method: "POST",
    headers,
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to save ports config: ${res.status}`);
  }
  return res.json();
}

export async function getCarrierOverrides(adminPassword?: string): Promise<Record<string, Record<string, string>>> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/carrier-overrides`, { headers });
  if (!res.ok) {
    throw new Error(`Failed to load carrier overrides: ${res.status}`);
  }
  return res.json();
}

export async function addCarrierOverride(
  carrier: string,
  key: string,
  overrideText: string,
  adminPassword?: string
): Promise<{ status: string }> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/carrier-overrides`, {
    method: "POST",
    headers,
    body: JSON.stringify({ carrier, key, override_text: overrideText }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to add carrier override: ${res.status}`);
  }
  return res.json();
}

export async function deleteCarrierOverride(
  carrier: string,
  key: string,
  adminPassword?: string
): Promise<{ status: string }> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/carrier-overrides`, {
    method: "DELETE",
    headers,
    body: JSON.stringify({ carrier, key }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to delete carrier override: ${res.status}`);
  }
  return res.json();
}

export async function getExchangeRates(adminPassword?: string): Promise<Record<string, { code: string; name: string; rate_per_usd: number; usd_per_unit: number; symbol: string }>> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/exchange-rates`, { headers });
  if (!res.ok) {
    throw new Error(`Failed to load exchange rates: ${res.status}`);
  }
  return res.json();
}

export async function updateExchangeRate(
  currency: string,
  rate_per_usd: number,
  adminPassword?: string
): Promise<{ status: string; currency: any }> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/exchange-rates`, {
    method: "POST",
    headers,
    body: JSON.stringify({ currency, rate_per_usd }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to update exchange rate: ${res.status}`);
  }
  return res.json();
}

export async function getUsers(adminPassword?: string): Promise<any[]> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/users`, { headers });
  if (!res.ok) {
    throw new Error(`Failed to load users: ${res.status}`);
  }
  return res.json();
}

export async function loginUser(name: string): Promise<any> {
  const res = await failoverFetch(`/api/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Login failed: ${res.status}`);
  }
  return res.json();
}

export async function validateSession(name: string): Promise<any> {
  const res = await failoverFetch(`/api/users/validate-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Session invalid: ${res.status}`);
  }
  return res.json();
}

export async function resetAllUsers(adminPassword?: string): Promise<{ status: string; message: string }> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/users/reset-all`, {
    method: "DELETE",
    headers,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to reset users: ${res.status}`);
  }
  return res.json();
}

export async function getSearchHistory(userName?: string): Promise<any[]> {
  const query = userName ? `?user_name=${encodeURIComponent(userName)}` : "";
  const res = await failoverFetch(`/api/admin/search-history${query}`);
  if (!res.ok) {
    throw new Error(`Failed to load search history: ${res.status}`);
  }
  return res.json();
}

export async function getRouteHealth(): Promise<any> {
  const res = await failoverFetch(`/api/admin/route-health`);
  if (!res.ok) {
    throw new Error(`Failed to load route health: ${res.status}`);
  }
  return res.json();
}

export async function parseRfq(
  text?: string,
  image_b64?: string,
  image_mime?: string
): Promise<RFQParseResult> {
  const res = await failoverFetch(`/api/rfq/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text || "", image_b64, image_mime }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `RFQ Parsing error: ${res.status}`);
  }
  return res.json();
}

export async function getCustomPorts(password?: string): Promise<any[]> {
  const res = await failoverFetch(`/api/admin/custom-ports`, {
    headers: password ? { "x-admin-password": password } : {},
  });
  if (!res.ok) {
    throw new Error(`Failed to load custom ports: ${res.status}`);
  }
  return res.json();
}

export async function addCustomPort(
  portData: { code: string; name: string; country: string; aliases?: string[] },
  password?: string
): Promise<any> {
  const res = await failoverFetch(`/api/admin/custom-ports`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(password ? { "x-admin-password": password } : {}),
    },
    body: JSON.stringify(portData),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to add/amend custom port: ${res.status}`);
  }
  return res.json();
}

export async function deleteCustomPort(code: string, password?: string): Promise<any> {
  const res = await failoverFetch(`/api/admin/custom-ports/${encodeURIComponent(code)}`, {
    method: "DELETE",
    headers: password ? { "x-admin-password": password } : {},
  });
  if (!res.ok) {
    throw new Error(`Failed to delete custom port: ${res.status}`);
  }
  return res.json();
}


