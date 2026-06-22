/**
 * API client for the Infreight Rate Automation backend.
 * Maps to the active FastAPI endpoints in /backend:
 *   POST /api/users/login          -> loginUser
 *   POST /api/rate-search          -> createRateSearch
 *   GET  /api/rate-search/{id}      -> getRateSearchResults
 *   POST /api/rate-search/{id}/release -> releaseRateSearch
 *   GET  /api/ports/suggest         -> getPortSuggestions
 *   GET  /health                    -> healthCheck
 */
import { API_URL } from '@/constants/api';
import type {
  RateSearchRequest,
  RateSearchCreateResponse,
  RateSearchResultResponse,
  UserSchema,
  PortSuggestion,
  VncStatus,
} from '@/types/api';

async function parseError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    return (data && (data.detail || data.message)) || fallback;
  } catch {
    return fallback;
  }
}

/** Find-or-create a user by name (name-only auth, mirrors the web LoginModal). */
export async function loginUser(name: string): Promise<UserSchema> {
  const res = await fetch(`${API_URL}/api/users/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    throw new Error(await parseError(res, `Login failed (${res.status})`));
  }
  return res.json();
}

export async function createRateSearch(
  request: RateSearchRequest,
): Promise<RateSearchCreateResponse> {
  const res = await fetch(`${API_URL}/api/rate-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(await parseError(res, `API error: ${res.status}`));
  }
  return res.json();
}

export async function getRateSearchResults(
  searchId: string,
): Promise<RateSearchResultResponse> {
  const res = await fetch(`${API_URL}/api/rate-search/${searchId}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export async function releaseRateSearch(searchId: string): Promise<void> {
  await fetch(`${API_URL}/api/rate-search/${searchId}/release`, { method: 'POST' });
}

export async function getPortSuggestions(
  query: string,
  limit = 5,
): Promise<PortSuggestion[]> {
  if (!query || query.length < 2) return [];
  const res = await fetch(
    `${API_URL}/api/ports/suggest?q=${encodeURIComponent(query)}&limit=${limit}`,
  );
  if (!res.ok) return [];
  return res.json();
}

export async function healthCheck(): Promise<{ status: string; mock_mode: boolean }> {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

/** noVNC viewer availability + per-carrier paths (for the in-app 2FA flow). */
export async function getVncStatus(): Promise<VncStatus> {
  const res = await fetch(`${API_URL}/api/vnc-status`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}
