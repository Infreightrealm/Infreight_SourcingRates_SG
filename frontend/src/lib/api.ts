/**
 * API client for the Infreight Rate Automation backend.
 */
import type { RateSearchRequest, RateSearchCreateResponse, RateSearchResultResponse, RFQParseResult, BatchSearchStatusItem } from "./types";


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

// Team Social (messaging) is pure DB CRUD with no Playwright/scraping dependency,
// so it's routed straight to the always-on cloud backend instead of the primary/
// backup failover pair used for rate search — that keeps the residential-IP worker
// laptop free of chat polling load. Defaults to the existing cloud backup URL
// (same DB, same auth sessions) since a dedicated env var is usually unnecessary;
// set NEXT_PUBLIC_SOCIAL_API_URL to point Social at a different backend instead.
const socialApiUrl = formatUrl(
  process.env.NEXT_PUBLIC_SOCIAL_API_URL || process.env.NEXT_PUBLIC_API_URL_BACKUP || ""
);

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
  const token = typeof window !== "undefined" ? localStorage.getItem("infreight_token") : null;
  const authHeaders: Record<string, string> = {};
  if (token) {
    authHeaders["Authorization"] = `Bearer ${token}`;
  }

  const headers = {
    ...defaultHeaders,
    ...authHeaders,
    ...options.headers,
  };

  const fetchOptions: RequestInit = {
    credentials: "include",
    ...options,
    headers,
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
    const res = await fetch(`${currentActiveUrl}${path}`, fetchOptions);
    if (!res.ok && res.status >= 500 && currentActiveUrl !== backupApiUrl) {
      const switched = doSwitchToBackup(`HTTP ${res.status} Server Error`);
      if (switched) {
        try {
          return await fetch(`${currentActiveUrl}${path}`, fetchOptions);
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
        return await fetch(`${currentActiveUrl}${path}`, fetchOptions);
      } catch (backupErr) {
        console.error(`[API] Backup URL ${backupApiUrl} also failed: ${backupErr}`);
        throw backupErr;
      }
    }
    throw primaryErr;
  }
}

// Dedicated fetch for Team Social — tries the cloud backend FIRST (so the
// residential-IP worker laptop doesn't carry chat-polling load in the normal
// case), but the cloud backend is still just a backup role-wise: if it's
// unreachable or erroring, fall through to whichever backend rate search is
// currently using (normally the laptop, which runs the identical Social code
// against the same DB) rather than leaving Social with no fallback at all.
// Which backend actually served the most recent Social request — surfaced in
// the UI so "is it really using cloud?" is answerable at a glance, not just
// by digging through DevTools.
let lastSocialMode: "cloud" | "fallback" | "unconfigured" = socialApiUrl ? "cloud" : "unconfigured";

export function getSocialConnectionInfo(): { mode: "cloud" | "fallback" | "unconfigured"; url: string } {
  return { mode: lastSocialMode, url: lastSocialMode === "fallback" ? currentActiveUrl : socialApiUrl };
}

async function socialFetch(path: string, options: RequestInit = {}): Promise<Response> {
  if (!socialApiUrl) {
    lastSocialMode = "unconfigured";
    return failoverFetch(path, options);
  }

  const token = typeof window !== "undefined" ? localStorage.getItem("infreight_token") : null;
  const authHeaders: Record<string, string> = {};
  if (token) {
    authHeaders["Authorization"] = `Bearer ${token}`;
  }

  const fetchOptions: RequestInit = {
    credentials: "include",
    ...options,
    headers: {
      ...defaultHeaders,
      ...authHeaders,
      ...options.headers,
    },
  };

  try {
    const res = await fetch(`${socialApiUrl}${path}`, fetchOptions);
    if (!res.ok && res.status >= 500) {
      console.warn(`[API] Social cloud backend ${socialApiUrl} returned ${res.status}. Falling back to ${currentActiveUrl}.`);
      lastSocialMode = "fallback";
      return failoverFetch(path, options);
    }
    lastSocialMode = "cloud";
    return res;
  } catch (err) {
    console.warn(`[API] Social cloud backend ${socialApiUrl} unreachable (${err}). Falling back to ${currentActiveUrl}.`);
    lastSocialMode = "fallback";
    return failoverFetch(path, options);
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

export async function createBatchRateSearch(payload: {
  routes: Array<{ origin: string; destination: string; container_types?: string[]; weight_per_container_kg?: number }>;
  carriers?: string[];
  user_name?: string;
  search_mode?: 'quick' | 'detailed';
  commodity?: string;
}): Promise<{ batch_id: string; total_routes: number; carriers: string[]; search_ids: string[]; status: string; deduplicated_routes?: number; warnings?: string[] }> {
  const res = await failoverFetch(`/api/rate-search/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Batch API error: ${res.status}`);
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

/** Lightweight bulk status for a whole batch (no quote payloads). */
export async function getBatchSearchStatus(searchIds: string[]): Promise<BatchSearchStatusItem[]> {
  if (searchIds.length === 0) return [];
  const res = await failoverFetch(`/api/rate-search/status?ids=${encodeURIComponent(searchIds.join(","))}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

/**
 * Polls an entire batch with ONE request per tick instead of one poller per route
 * (168 routes x a 2s poller each was ~84 req/s), and is bounded by wall-clock time
 * rather than an attempt count — a 168-route x 7-carrier batch runs far longer than
 * the old 450-attempt (15 min) cap, after which the UI silently stopped updating
 * while the backend kept working.
 *
 * `onRouteTerminal` fires exactly once per search the first time it is seen terminal,
 * so the caller can fetch that route's full results just once.
 */
export async function pollBatchSearchStatus(
  searchIds: string[],
  onTick: (items: BatchSearchStatusItem[]) => void,
  onRouteTerminal: (searchId: string) => Promise<void> | void,
  opts: { intervalMs?: number; maxDurationMs?: number } = {},
): Promise<BatchSearchStatusItem[]> {
  const intervalMs = opts.intervalMs ?? 4000;
  const maxDurationMs = opts.maxDurationMs ?? 4 * 60 * 60 * 1000; // 4 hours
  const started = Date.now();
  const terminalSeen = new Set<string>();
  let last: BatchSearchStatusItem[] = [];

  return new Promise((resolve) => {
    const tick = async () => {
      try {
        last = await getBatchSearchStatus(searchIds);
        onTick(last);
        for (const item of last) {
          if (item.is_terminal && !terminalSeen.has(item.search_id)) {
            terminalSeen.add(item.search_id);
            try {
              await onRouteTerminal(item.search_id);
            } catch (e) {
              console.warn("onRouteTerminal failed for", item.search_id, e);
            }
          }
        }
      } catch (e) {
        console.warn("Batch status poll failed (will retry):", e);
      }
      const allDone = last.length === searchIds.length && last.every((i) => i.is_terminal);
      const timedOut = Date.now() - started >= maxDurationMs;
      if (allDone || timedOut) {
        clearInterval(timer);
        resolve(last);
      }
    };
    const timer = setInterval(tick, intervalMs);
    void tick();
  });
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

export interface AuthUser {
  id: string;
  username: string;
  display_name: string;
  name: string;
  role: "admin" | "user";
  status: "active" | "pending" | "disabled";
  is_active: boolean;
  avatar_url?: string | null;
  title_or_role_desc?: string | null;
  created_at?: string;
  approved_at?: string;
  approved_by?: string;
  last_login_at?: string;
  needs_password?: boolean;
}

export async function loginAuth(
  username: string,
  password: string
): Promise<{ user: AuthUser; token?: string; message?: string }> {
  const res = await failoverFetch(`/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // If backend reports legacy account needs password setup
    if (res.status === 428 || data?.detail?.code === "NEEDS_PASSWORD") {
      const err: any = new Error(data?.detail?.message || "Password setup required");
      err.code = "NEEDS_PASSWORD";
      err.username = data?.detail?.username || username;
      err.displayName = data?.detail?.display_name || username;
      throw err;
    }
    throw new Error(data.detail || data.error || "Incorrect username or password.");
  }
  if (data.token && typeof window !== "undefined") {
    localStorage.setItem("infreight_token", data.token);
    localStorage.setItem("userName", data.user.display_name || data.user.name || data.user.username);
  }
  return data;
}

export async function signupAuth(
  displayName: string,
  username: string,
  password: string
): Promise<{ user: AuthUser; token?: string; message?: string }> {
  const res = await failoverFetch(`/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ displayName, username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.error || "Failed to create account request.");
  }
  if (data.token && typeof window !== "undefined") {
    localStorage.setItem("infreight_token", data.token);
    localStorage.setItem("userName", data.user.display_name || data.user.name || data.user.username);
  }
  return data;
}

export async function setupPasswordAuth(
  username: string,
  password: string,
  confirmPassword?: string
): Promise<{ user: AuthUser; token?: string; message?: string }> {
  const res = await failoverFetch(`/api/auth/setup-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, confirm_password: confirmPassword || password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.error || "Failed to set up password.");
  }
  if (data.token && typeof window !== "undefined") {
    localStorage.setItem("infreight_token", data.token);
    localStorage.setItem("userName", data.user.display_name || data.user.name || data.user.username);
  }
  return data;
}

export async function getMe(): Promise<{ user: AuthUser }> {
  const res = await failoverFetch(`/api/auth/me`);
  if (!res.ok) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("infreight_token");
    }
    throw new Error(`Unauthenticated: ${res.status}`);
  }
  const data = await res.json();
  if (data?.user && typeof window !== "undefined") {
    localStorage.setItem("userName", data.user.display_name || data.user.name || data.user.username);
  }
  return data;
}

export async function logoutAuth(): Promise<void> {
  try {
    await failoverFetch(`/api/auth/logout`, { method: "POST" });
  } finally {
    if (typeof window !== "undefined") {
      localStorage.removeItem("infreight_token");
      localStorage.removeItem("userName");
    }
  }
}

export async function getAdminOverview(adminPassword?: string): Promise<{
  users: AuthUser[];
  stats: {
    totalUsers: number;
    activeUsers: number;
    pendingUsers: number;
    totalSearches: number;
    totalQuotes: number;
  };
  audit: {
    id: string;
    at: string;
    actor: string;
    action: string;
    detail: string;
  }[];
  me: AuthUser;
}> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await failoverFetch(`/api/admin/overview`, { headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch admin overview: ${res.status}`);
  }
  return res.json();
}

export async function adminUserAction(
  userId: string,
  action: "approve" | "reject" | "disable" | "enable" | "role" | "password" | "delete",
  payload: any = {},
  adminPassword?: string
): Promise<any> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const method = action === "delete" ? "DELETE" : "POST";
  const path = action === "delete" ? `/api/admin/users/${encodeURIComponent(userId)}` : `/api/admin/users/${encodeURIComponent(userId)}/${action}`;
  const res = await failoverFetch(path, {
    method,
    headers,
    body: Object.keys(payload).length > 0 ? JSON.stringify(payload) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.error || `Action ${action} failed: ${res.status}`);
  }
  return data;
}

export async function getSearchHistory(userName?: string, limit: number = 5000): Promise<any[]> {
  const params = new URLSearchParams();
  if (userName) params.append("user_name", userName);
  params.append("limit", limit.toString());
  const res = await failoverFetch(`/api/admin/search-history?${params.toString()}`);
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

export async function getAdminAnalytics(params?: {
  timeRange?: string;
  userName?: string;
  carrier?: string;
}): Promise<any> {
  const query = new URLSearchParams();
  if (params?.timeRange) query.append("time_range", params.timeRange);
  if (params?.userName && params.userName !== "all") query.append("user_name", params.userName);
  if (params?.carrier && params.carrier !== "all") query.append("carrier", params.carrier);

  const qs = query.toString() ? `?${query.toString()}` : "";
  const res = await failoverFetch(`/api/admin/analytics${qs}`);
  if (!res.ok) {
    throw new Error(`Failed to load consolidated analytics: ${res.status}`);
  }
  return res.json();
}

export async function parseRfq(
  text?: string,
  image_b64?: string,
  image_mime?: string,
  model?: string
): Promise<RFQParseResult> {
  const res = await failoverFetch(`/api/rfq/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text || "", image_b64, image_mime, model }),
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

export interface Colleague {
  id: string;
  username: string;
  display_name: string;
  name: string;
  role: string;
  title_or_role_desc?: string;
  avatar_url?: string | null;
  is_self: boolean;
  unread_count: number;
  last_message?: {
    content: string | null;
    created_at: string | null;
    is_from_me: boolean;
  } | null;
  stats: {
    total_searches: number;
    top_lanes: Array<{ origin: string; destination: string; count: number }>;
    last_searched_at: string | null;
  };
}

export interface DirectMessageItem {
  id: string;
  sender_id: string;
  recipient_id: string;
  content: string;
  attachment_url?: string | null;
  attachment_type?: string | null;
  message_type?: "text" | "poke";
  created_at: string | null;
  read_at: string | null;
  is_from_me: boolean;
}

export async function getColleagues(): Promise<Colleague[]> {
  const res = await socialFetch(`/api/social/colleagues`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to load team colleagues.");
  }
  return res.json();
}

export async function getConversation(colleagueId: string): Promise<DirectMessageItem[]> {
  const res = await socialFetch(`/api/social/messages/${colleagueId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to load messages.");
  }
  return res.json();
}

export async function sendDirectMessage(
  recipientId: string,
  content: string,
  attachment?: { url: string; type: string } | null,
): Promise<DirectMessageItem> {
  const res = await socialFetch(`/api/social/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      recipient_id: recipientId,
      content,
      attachment_url: attachment?.url ?? null,
      attachment_type: attachment?.type ?? null,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to send message.");
  }
  return res.json();
}

export async function uploadUserAvatar(userId: string, avatarUrl: string): Promise<{ status: string; avatar_url: string }> {
  const res = await socialFetch(`/api/social/users/${userId}/avatar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ avatar_url: avatarUrl }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to upload avatar.");
  }
  return res.json();
}

export async function pokeColleague(recipientId: string): Promise<DirectMessageItem> {
  const res = await socialFetch(`/api/social/poke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipient_id: recipientId }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to send poke.");
  }
  return res.json();
}

export async function wipeConversation(colleagueId: string): Promise<{ status: string; deleted: number }> {
  const res = await socialFetch(`/api/social/messages/${colleagueId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to wipe conversation.");
  }
  return res.json();
}



