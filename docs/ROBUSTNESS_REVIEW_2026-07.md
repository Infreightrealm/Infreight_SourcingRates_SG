# Scraper Robustness Review — July 2026

Scope: `backend/carriers/*` (7 connectors, ~16k LOC), the shared base class, the job
scheduler, the batch/quick-search path, and the frontend batch driver. Every number
below was measured on `main` @ `3fa60c0`; every finding cites a file.

## 1. What was measured

| Connector | Lines | Silent `except` | Fixed sleeps | `inner_text()` parses | Blind "first input" fallbacks |
|---|---:|---:|---:|---:|---:|
| Hapag-Lloyd | 4,138 | 74 | 15 | 9 | 5 |
| Maersk | 3,350 | 55 | 65 | 21 | 0 |
| OOCL | 2,211 | 37 | 31 | 18 | 0 |
| ONE | 2,140 | 34 | 40 | 20 | 0 |
| CMA CGM | 2,101 | 26 | 37 | 25 | 0 |
| GreenX | 1,156 | 24 | 17 | 11 | 0 |
| MSC | 868 | 14 | 11 | 17 | 1 |
| **Total** | **16,964** | **264** | **216** | **121** | **6** |

Hashed CSS-module selectors (break on every carrier front-end deploy): **1** —
`button.NewQuoteSummary_breakdown-button__oIAYJ` in `one_connector.py`.

## 2. Why the scrapers break when a site changes

**F1 — The self-healing subsystem has zero adoption (highest leverage).**
`backend/agent/safe_step.py` wraps a Playwright action, detects bot challenges,
consults human-approved selector patches (`agent/selector_memory.py`), asks the AI
repair agent for a replacement selector, writes a repair report, and surfaces it in
the admin UI (`/api/connector-repair/*`, `SelfHealingAlerts.tsx`). **No connector
imports it.** `data/selector_memory.json` has never been created. Every mechanism the
codebase has for surviving a layout change is dead code from the scrapers' point of
view. Adopting it at the 5–8 highest-risk steps per connector (login submit, port
autocomplete pick, search submit, results wait, breakdown open) is the single
biggest robustness gain available, and it needs no new infrastructure.

**F2 — 264 silent `except` blocks make "layout changed" indistinguishable from
"no rates".** A selector that stops matching becomes `NO_QUOTES_AVAILABLE` with no
signal. This is why regressions this month (ONE 0-quotes, GreenX false "No Quotes",
Maersk per-type "sold out") were found by users looking at the VNC, not by the
system. Introduce a distinct `LAYOUT_CHANGED` outcome: zero cards found while the
page visibly contains prices/USD text is drift, not emptiness.

**F3 — 216 fixed sleeps.** Timing-dependent waits are both the slowness and the
flakiness: they fail under load and over-wait when the site is fast. Every one that
precedes an active-detection loop is redundant (three such 3–8s sleeps were removed
from Hapag on 2026-07-02); the rest should become `wait_until(predicate)`.

**F4 — ~121 layout-coupled `inner_text()` regex parses, interleaved with
page-driving code.** Parsing cannot be regression-tested against saved HTML because
it is not separable from the browser session. Every ONE regression this month
(the vertical-vs-horizontal breakdown, the triple-counted totals) was this class.
Separate *fetch* (returns text/HTML) from *parse* (pure function), and turn the
`scratch/*.html` dumps the connectors already write into golden-file tests.

**F5 — Cross-cutting logic is re-implemented per connector.** Per-cycle caching,
the sold-out rule, container-type splitting, modal dismissal, CAPTCHA waiting and
profile cloning each exist in up to seven variants. Bugs fixed in one recur in
another: the Maersk cache-key regression, the sold-out rule applied to ONE and Maersk
separately, GreenX's synchronous splitter silently dropped by the async base loop.
Lift them into `BaseCarrierConnector` (this change started that with
`build_quick_quotes`, `_split_or_none`, `_run_batch_route`, `_reset_between_routes`).

**F6 — Blind fallbacks type into whatever is first.** Hapag has five
`locator('input').first`-style fallbacks; one typed a port code into the login
email field on a session-expiry redirect. Policy: never act on an element whose
role was not verified; fail the step (into `safe_step`) instead.

**F7 — Hashed and framework-internal selectors.** One CSS-module hash (ONE) and a
reliance on framework classes (`.ag-row`, `mc-option`, `el-dialog`). Prefer role,
label, placeholder and visible-text anchors; keep class selectors as the *last*
fallback in an ordered list, and log which fallback matched so drift is visible
before it becomes an outage.

**F8 — No synthetic canary.** `/api/admin/route-health` exists; nothing feeds it on a
schedule. A nightly known-good lane per carrier, alerting on status drift, would
catch most layout changes before a customer RFQ does.

## 3. Multi-port quick search — defects found and fixed

| # | Defect | Effect | Status |
|---|---|---|---|
| Q1 | Card **summary** price stamped on every container type; on multi-container cards that is the sum across sizes | 20' and 40' identical and inflated; tariff sheet `Math.min` corrupted across carriers | **Fixed** — per-type via one breakdown per window |
| Q2 | ONE/GreenX hooks hardcoded `["DRY 20","DRY 40"]` | Requested 40HQ never returned | **Fixed** |
| Q3 | `carrier_lock` released before the batch actually ran | No profile-collision protection in batch mode | **Fixed** |
| Q4 | No per-route timeout/retry/session re-check | One hung route stalled 168; session expiry killed the rest | **Fixed** (`BATCH_ROUTE_TIMEOUT_SEC`, 1 retry, re-login) |
| Q5 | 168 pollers × 2s ≈ 84 req/s on the 3-level eager-load endpoint | DB hot-spot | **Fixed** — bulk status endpoint, one poll/tick |
| Q6 | Poll cap of 450 attempts (15 min) | UI froze while the backend kept working | **Fixed** — wall-clock bound (4h) |
| Q7 | 2ND HALF (15–28d) tariff columns hardcoded empty | Half the customer sheet never filled | **Fixed** — cheapest per window, bucketed by ETD |
| Q8 | Duplicate/typo ports ran as separate routes; frontend dedupe was exact-string only | Wasted carrier time; mislabeled rows | **Fixed** — LOCODE + name-similarity dedupe, pre-flight warnings |
| Q9 | GreenX sync splitter `await`ed in the batch loop | Detailed-mode batch for GreenX returned nothing | **Fixed** — `_split_or_none` |
| Q10 | `batch_id` returned but never persisted; resume relies on URL `search_ids` | Batches aren't listable/reloadable server-side | Recommended — a `batch` row or `batch_id` column |

Port resolution note: `search_port()` returns a confident hit for almost any string
(`SAKASTOON` → Sasstown, Liberia; `AL-SOKHNA` → Balakhna, Russia). The dedupe
therefore never trusts the LOCODE alone, and the batch response now carries
`warnings` for names that barely resemble the port they resolved to — so a bad
spelling in a 168-port list is caught before it costs seven carriers a route each.

## 4. Ranked recommendations

1. **Adopt `safe_step` at the top 5–8 steps per connector** (F1). Highest impact, no
   new infra; turns silent failures into reviewed repairs.
2. **Add a `LAYOUT_CHANGED` outcome and stop swallowing exceptions in the results
   path** (F2). Makes drift observable in the UI and Railway logs.
3. **Separate parse from fetch; add golden-file tests from `scratch/` dumps** (F4).
   Prevents the parsing-regression class entirely; CI catches it before deploy.
4. **Ordered, role-first selector lists with match telemetry** (F7, F6). Replace the
   CSS-module hash and blind fallbacks first.
5. **Lift the remaining per-connector duplicates into the base class** (F5): cycle
   cache, sold-out rule, modal dismissal, CAPTCHA wait, profile clone/sync.
6. **Nightly canary lanes feeding `/admin/route-health`** (F8).
7. **Persist batches** (Q10).
8. **Convert remaining fixed sleeps to condition waits, carrier by carrier** (F3) —
   worthwhile, but lower risk-reduction per hour than the items above.

## 5. Verification of this change
- 7 unit tests for the quick path and batch loop pass (per-window selection,
  per-type pricing, requested types respected, sync splitter, single-type-only
  fallback, both windows populated, timeout → retry → continue).
- `tsc --noEmit` clean after the frontend changes.
- Dedupe/warning rule checked against live `search_port` data.
