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

const primaryApiUrl = formatUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
const backupApiUrl = formatUrl(process.env.NEXT_PUBLIC_API_URL_BACKUP || "");

export let API_URL = primaryApiUrl;

let currentActiveUrl = primaryApiUrl;
let onUrlSwitchCallback: ((url: string) => void) | null = null;

export function getApiUrl(): string {
  return currentActiveUrl;
}

export function registerUrlSwitchCallback(cb: (url: string) => void) {
  onUrlSwitchCallback = cb;
}

// Custom fetch wrapper with automatic failover
async function failoverFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  try {
    const res = await fetch(`${currentActiveUrl}${path}`, { ...options, headers });
    return res;
  } catch (primaryErr) {
    if (backupApiUrl && currentActiveUrl !== backupApiUrl) {
      console.warn(`[API] Primary URL ${currentActiveUrl} failed: ${primaryErr}. Switching to backup: ${backupApiUrl}`);
      currentActiveUrl = backupApiUrl;
      API_URL = backupApiUrl;
      if (onUrlSwitchCallback) {
        try {
          onUrlSwitchCallback(backupApiUrl);
        } catch (cbErr) {
          console.error("Error in URL switch callback:", cbErr);
        }
      }
      try {
        const res = await fetch(`${currentActiveUrl}${path}`, { ...options, headers });
        return res;
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

        const terminalStatuses = ["COMPLETED", "PARTIAL_COMPLETED", "FAILED"];
        if (terminalStatuses.includes(data.status) || attempts >= maxAttempts) {
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

export async function parseRfq(text: string): Promise<RFQParseResult> {
  const res = await failoverFetch(`/api/rfq/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `RFQ Parsing error: ${res.status}`);
  }
  return res.json();
}

