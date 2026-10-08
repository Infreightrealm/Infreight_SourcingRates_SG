import type { QuoteSchema } from "./types";

export type RoutingLabel = "Direct" | "Transit";

/** UN/LOCODE in a port string: bracketed ("AL 'AQABAH [JOAQJ]") or a bare all-caps code ("JOAQJ"), so "Aqaba" isn't one. */
function locodeOf(s: string): string | null {
  const bracketed = s.match(/[[(]\s*([A-Za-z]{2}[A-Za-z0-9]{3})\s*[\])]/);
  if (bracketed) return bracketed[1].toUpperCase();
  const bare = s.trim();
  return /^[A-Z]{2}[A-Z0-9]{3}$/.test(bare) ? bare : null;
}

/** "Al 'Aqabah, Jordan [JOAQJ]" -> "aqabah": the place name only, without articles or punctuation. */
function placeName(s: string): string {
  return s
    .split(/[,[(]/)[0]
    .toLowerCase()
    .replace(/^(al|el|port of|port)\s+/, "")
    .replace(/[^a-z]/g, "");
}

/** Close enough to be the same port: one name contains the other, or they differ by one or two letters (Aqaba / Aqabah). */
function similarNames(a: string, b: string): boolean {
  if (!a || !b) return false;
  if (a.includes(b) || b.includes(a)) return true;
  const dp = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) dp[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return dp[a.length][b.length] <= Math.max(1, Math.floor(Math.min(a.length, b.length) / 4));
}

/** True when `port` names the destination itself. */
export function isDestinationPort(port: string, destination: string | null | undefined): boolean {
  if (!destination) return false;
  const a = locodeOf(port);
  const b = locodeOf(destination);
  if (a && b) return a === b;
  return similarNames(placeName(port), placeName(destination));
}

/**
 * Routing as the team quotes it: "Direct" or "Transit". A carrier's routing text
 * that is just the destination port (e.g. MSC's "AL 'AQABAH [JOAQJ]") is Direct;
 * any other port named there, or "via ...", is a transshipment.
 */
export function routingLabel(q: Pick<QuoteSchema, "routing" | "port_of_discharge">, destination: string | null | undefined): RoutingLabel {
  const routing = (q.routing ?? "").trim();
  const lower = routing.toLowerCase();
  if (lower === "direct" || lower === "") {
    // No transshipment named; a discharge port elsewhere than the destination still means a transit.
    const pod = (q.port_of_discharge ?? "").trim();
    return !pod || pod.toLowerCase() === "direct" || isDestinationPort(pod, destination) ? "Direct" : "Transit";
  }
  if (/transit|^via\b|transship|t\/s/.test(lower)) return "Transit";
  const ports = routing.split(/\s*(?:,|;|\s-\s|→|->|\/)\s*/).filter(Boolean);
  return ports.every((p) => isDestinationPort(p, destination)) ? "Direct" : "Transit";
}

/** The transshipment ports to show next to "Transit", if the carrier named any. */
export function transitVia(q: Pick<QuoteSchema, "routing">, destination: string | null | undefined): string | null {
  const routing = (q.routing ?? "").trim();
  if (!routing || /^(direct|transit)$/i.test(routing)) return null;
  const ports = routing
    .replace(/^via\s+/i, "")
    .split(/\s*(?:,|;|\s-\s|→|->|\/)\s*/)
    .filter((p) => p && !isDestinationPort(p, destination) && !/transshipment port/i.test(p));
  return ports.length ? ports.join(", ") : null;
}
