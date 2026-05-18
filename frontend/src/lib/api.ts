/**
 * API client for the Infreight Rate Automation backend.
 */
import type { RateSearchRequest, RateSearchCreateResponse, RateSearchResultResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
