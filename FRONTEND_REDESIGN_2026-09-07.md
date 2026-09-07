# Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)

**Branch:** `claude/frontend-mockup-styling-ma1esp`
**Commits:** `082b43a` (design system) → `21ade75` (workspace + intro) → `2f9d92b` (fixes)
**Scope:** `frontend/` only — 35 files, +3212 / −699
**Status:** ✅ Implemented, browser-verified, pushed. Not yet merged to `main`, no PR opened.

> **Handoff note for other agents/IDEs:** the single most important thing to carry
> forward is that colour, radius, elevation and motion now come from **semantic
> tokens** in `frontend/src/app/globals.css`. Do not reintroduce hard-coded
> `slate-700 dark:text-white/80`-style pairs — see *Conventions* at the bottom and
> `frontend/AGENTS.md`.

---

## 0. The one invariant

**No backend change. None.** No endpoint, request payload, response handling, state
machine or polling path was modified, and nothing outside `frontend/` was touched.
Verified by diffing with all `class`/`className` attributes stripped — the only
behavioural deltas in the whole redesign were:

- `LoginModal`: `disabled={!name.trim()}` → `disabled={!name.trim() || loading}` (blocks double-submit)
- `CarrierMultiSelect`: an arrow function changed from implicit to block body to compute a local
- `RateSearchForm`: gained an **optional** `onRouteChange` callback (submission untouched)
- `PortAutocomplete`: suggestions now gated on user edit (see §4)

Everything else is presentation.

---

## 1. Design system foundation (`082b43a`)

Adopted the token contract from [componentry.dev](https://componentry.dev)
(`harshjdhv/componentry`, MIT) — a **copy-paste** library, not a runtime dependency.
Retuned to the Infreight marine palette.

### `frontend/src/app/globals.css` — the whole theming surface

Defines, for light and dark:

| Group | Tokens |
|---|---|
| Surfaces | `--background` `--card` `--popover` `--foreground` + `-foreground` pairs |
| Brand | `--primary` `--brand-from` `--brand-to` |
| Neutrals | `--secondary` `--muted` `--accent` (+ foregrounds) |
| Semantic | `--success` `--warning` `--destructive` `--info` (+ foregrounds) |
| Lines/focus | `--border` `--line` `--input` `--ring` |
| Elevation | `--shadow-card` `--shadow-card-hover` `--shadow-panel` `--shadow-brand` `--surface-inset` |
| Motion | `--ease-out-strong` `--ease-in-out-strong` |
| Data-viz | `--chart-1` … `--chart-5` |

All mapped through `@theme inline`, so `bg-card`, `text-muted-foreground`,
`border-border`, `shadow-card`, `rounded-lg` etc. resolve from them.

### New primitives — `frontend/src/components/ui/`

Owned in-repo, adapted from Componentry:

- `button.tsx` — cva variants (`default` `brand` `destructive` `outline` `secondary` `ghost` `link`)
- `input.tsx` — `Input`, `Textarea`, `Label`, plus exported `fieldClassName` / `labelClassName` strings
  so existing raw `<input>`/`<select>` elements can adopt the look without restructuring
- `card.tsx` — `Card` (variants `default` `glass` `subtle` `info` `success` `warning` `destructive`) + subcomponents
- `badge.tsx` — `Badge`, `Dot`
- `surfaces.tsx` — `Overlay`, `Panel`, `Separator`, `Skeleton`, `SectionHeading`
- `shimmer-button.tsx` — Componentry's conic-spark CTA (used for **Search Rates**)
- `pulsating-button.tsx`, `kbd.tsx`

`frontend/src/lib/utils.ts` provides `cn()` (clsx + tailwind-merge) and motion easing constants.

### Dependencies added (5, all small, no runtime lib dependency on Componentry)

```
@radix-ui/react-slot  ^1.3.3
class-variance-authority ^0.7.1
clsx                  ^2.1.1
tailwind-merge        ^3.6.0
tw-animate-css        ^1.4.0
```

### Migration performed

**924 hard-coded colour utilities** (`slate-*` / `gray-*` / `dark:bg-[#hex]` /
`dark:text-white/40` and friends) replaced with semantic roles across every component and
the admin registry — `admin/page.tsx` alone carried 147 pairs. 25 literal colours remain
by design: the modal scrims (`bg-slate-950/50`), the emerald→teal export-button gradient,
and white text sitting on brand gradients. Emoji in controls swapped for the
already-bundled Lucide glyphs.

---

## 2. Bugs found and fixed during the restyle

These were **pre-existing defects**, not regressions:

1. **27 animation/interaction utility classes had no keyframes.** `animate-fade-in-up`
   (28 call sites), `btn-interactive` (19), `shine-on-hover`, `orbit-spinner`,
   `animate-shimmer`, `focus-glow`, `stagger-1..6`, `row-enter` and the rest were
   referenced throughout the components but never defined in the stylesheet — every
   entrance, skeleton and button interaction was silently inert. All defined now, on one pair of easing curves, and the whole library
   collapses under `prefers-reduced-motion`.

2. **`BackendConfigModal` was pinned dark** (`bg-slate-900 text-white`) and rendered
   white-on-white in light mode. Now reads from `--popover`.

3. **Stacking-context trap (regression I introduced, then fixed).** Restoring
   `animate-fade-in-up` gave each form row a *held* `transform` via
   `animation-fill-mode: both`, and with it a stacking context that trapped the port
   suggestions dropdown behind the row below. Fixed at the keyframe level — entrance
   animations now settle on `transform: none` — plus `relative z-20` on the route row.
   **If you add entrance animations near an overlay, remember this.**

---

## 3. Workspace + launch intro (`21ade75`)

### `frontend/src/lib/preferences.ts` — client-only preference store

Versioned `localStorage` store (`infreight.workspace.v1`) on `useSyncExternalStore`.
SSR-safe, tolerant of blocked/corrupt site data, synced across tabs. Shape:

```ts
{ version, accent, density, panels: { rfq, liveViewer, assistant }, lanes: SavedLane[], introSeen }
```

**This never reaches the backend.** Preferences are per-browser, not per-user-account —
see *Known limitations*.

### `WorkspacePanel.tsx` — four customization cards (header → "Workspace")

| Card | What it does |
|---|---|
| **Your activity** | Searches run, quotes returned, share returning ≥1 quote, distinct lanes, a 14-day per-day chart with hover readout, most-searched lanes. **Derived client-side** from the existing `GET /api/admin/search-history` response (`UsageStats.tsx`). No new endpoint. |
| **Saved lanes** | Pin the route currently in the form; click a pinned lane to load it back. Restores the exact `City, Country [LOCODE]` strings the payload expects. |
| **Appearance** | Theme (next-themes), 5 accents, rates-grid density. |
| **Panels** | Hide the RFQ email reader, live browser viewer, or assistant launcher. |

**How accents work:** the panel stamps `data-accent` / `data-density` on `<html>`;
`globals.css` re-points only `--primary`, `--brand-from/to`, `--ring`, `--shadow-brand`
per accent. **No component file knows an accent exists.** Each accent has separately
tuned light and dark steps.

`RateSearchForm` gained an optional `onRouteChange` callback so a route can be pinned
as it's typed, before any search runs.

### `LaunchIntro.tsx`

First-visit-only branded sequence (~2.6 s): mark springs in → horizon rule draws →
wordmark rises. Gated by `introSeen` in localStorage. Skippable by click, Escape or
button; replayable from the Workspace panel; **skipped outright** under
`prefers-reduced-motion`.

> **Gotcha for future edits:** writing the `introSeen` flag flips the prop the start
> effect depends on. The effect re-ran, its cleanup killed the finish timer, and the
> veil stuck on screen permanently. The decision is now latched in a ref and timers
> tear down on unmount only. Don't "simplify" that back.

---

## 4. Follow-up fixes (`2f9d92b`)

- **Port dropdown opened over the form on load.** `PortAutocomplete` fetched and opened
  its panel for *any* value it was handed, not just typed ones — so a restored search, a
  parsed RFQ or a pinned lane popped both dropdowns open, covering the container and
  weight rows. Suggestions are now gated on an actual edit (`userEditedRef`), which also
  drops two requests from every page load. Typing behaves exactly as before. *(Pre-existing.)*
- Header title wrapped once the Workspace button joined the control row — title holds its
  line, subtitle drops below `xl`.

---

## 5. Verification

| Check | Result |
|---|---|
| `npm run build` (Next 16.2.6 / Turbopack) | ✅ passes |
| TypeScript | ✅ passes |
| ESLint | **83 → 80 problems**, none introduced (all remaining are pre-existing `no-explicit-any` in `api.ts` / `excelExport.ts` / `admin/page.tsx`) |
| Browser pass (Playwright, mocked backend) | quote drawer, both modals, workspace panel, theme toggle, carrier + container toggles, port autocomplete, sort/filter controls, admin gate — all green, 0 console errors |
| Preference persistence | accent / density / panels / lanes survive reload ✅ |
| Intro gating | plays once, auto-dismisses, suppressed on revisit, replays on demand ✅ |
| Port value contract | pin → clear → load restores `"Singapore, Singapore [SGSIN]"` verbatim ✅ |

---

## 6. Known limitations / candidate follow-ups

1. **Preferences are per-browser, not per-user.** A user on a second machine starts
   fresh. Fixing this means persisting against the user record — a **backend change**,
   deliberately not done here.
2. **`SelfHealingAlerts` throws `.filter is not a function`** when the repair-reports
   endpoint returns a non-array. Pre-existing; not touched because it's data handling,
   not presentation.
3. **Chat launcher overlaps content.** The FAB at `fixed bottom-6 left-6` can sit over
   the Origin field at certain scroll positions — inherent to a floating action button;
   left alone pending a call on moving it.
4. The activity figures and rate rows in any screenshots are **stubbed** (no backend in
   the capture environment). The shapes are real; the values are placeholders.

---

## 7. Conventions to follow from here

**Do:**
- Use semantic tokens: `bg-card`, `text-foreground`, `text-muted-foreground`,
  `border-border`, `bg-muted`, `shadow-card`, `text-success-foreground`,
  `bg-warning/12`, `text-destructive-foreground`.
- Reach for `frontend/src/components/ui/*` before hand-rolling a button/card/badge/input.
- Use `cn()` from `@/lib/utils` for conditional classes.
- Keep new preference state in `lib/preferences.ts`; it is client-only by design.

**Don't:**
- Reintroduce `slate-*` / `dark:bg-[#hex]` pairs — they break the accent system and
  the light/dark contract.
- Hard-code a brand colour; use `--primary` / `bg-gradient-brand` so accents follow.
- Add an entrance animation whose final keyframe holds a real `transform` near an
  overlay (see §2.3).

**Reference:** carrier brand hexes in `lib/types.ts` (`CARRIERS`) are intentionally
*outside* the token set — they are the shipping lines' own marks, not theme colour.
Note that `MAERSK #004B8D` and `CMA_CGM #002B5C` are near-identical navies, so never
encode carrier identity by colour alone; always pair with the name.
