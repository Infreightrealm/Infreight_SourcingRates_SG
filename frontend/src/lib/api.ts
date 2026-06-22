/**
 * API client for the Infreight Rate Automation backend.
 */
import type { RateSearchRequest, RateSearchCreateResponse, RateSearchResultResponse } from "./types";

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_URL = (rawApiUrl && !rawApiUrl.startsWith("http://") && !rawApiUrl.startsWith("https://"))
  ? `https://${rawApiUrl}`
  : rawApiUrl;

export async function createRateSearch(request: RateSearchRequest): Promise<RateSearchCreateResponse> {
  const res = await fetch(`${API_URL}/api/rate-search`, {
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
  const res = await fetch(`${API_URL}/api/rate-search/${searchId}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
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
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

export async function getPortSuggestions(query: string, limit = 5): Promise<any[]> {
  if (!query || query.length < 2) return [];
  const res = await fetch(`${API_URL}/api/ports/suggest?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function forceStopSearches(): Promise<{status: string, message: string}> {
  const res = await fetch(`${API_URL}/api/force-stop`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to force stop searches");
  return res.json();
}

export async function getCountriesMap(): Promise<Record<string, string>> {
  const res = await fetch(`${API_URL}/api/ports/countries`);
  if (!res.ok) return {};
  return res.json();
}

export async function getPortsConfig(adminPassword?: string): Promise<{ popular_ports: string[]; boosted_countries: string[] }> {
  const headers: Record<string, string> = {};
  if (adminPassword) {
    headers["x-admin-password"] = adminPassword;
  }
  const res = await fetch(`${API_URL}/api/admin/config/ports`, { headers });
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
  const res = await fetch(`${API_URL}/api/admin/config/ports`, {
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
