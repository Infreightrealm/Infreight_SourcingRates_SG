<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

<!-- BEGIN:infreight-design-system -->
# Design system — read before touching any UI

Since 2026-09-07 this frontend runs on a semantic token layer adapted from
componentry.dev. Full write-up: `../FRONTEND_REDESIGN_2026-09-07.md`.

## Use tokens, not raw colours

Colour, radius, elevation and motion are defined once in `src/app/globals.css`
and consumed by role:

| Instead of | Use |
|---|---|
| `text-slate-900 dark:text-white` | `text-foreground` |
| `text-slate-500 dark:text-white/40` | `text-muted-foreground` |
| `bg-white dark:bg-[#121212]` | `bg-card` (or `bg-popover` for overlays) |
| `border-slate-200 dark:border-white/10` | `border-border` (hairlines: `border-line`) |
| `bg-emerald-500/10 text-emerald-600 …` | `bg-success/12 text-success-foreground` |
| amber / rose equivalents | `warning` / `destructive` the same way |
| `bg-blue-600` for the brand | `bg-primary` or `bg-gradient-brand` |

Hard-coding a colour pair breaks two things: the light/dark contract, and the
five user-selectable accents (which re-point `--primary` / `--brand-from` /
`--brand-to` / `--ring` only).

## Reuse the primitives

`src/components/ui/` holds `Button`, `Input`/`Textarea`/`Label`, `Card`, `Badge`,
`Dot`, `Kbd`, `ShimmerButton`, `PulsatingButton`, and `Overlay`/`Panel`/
`Separator`/`Skeleton`/`SectionHeading`. Prefer these over new one-off markup.
Merge classes with `cn()` from `@/lib/utils`.

## Two traps that have already bitten

1. **Entrance animations create stacking contexts.** `animation-fill-mode: both`
   holds the final keyframe forever, so a final `transform: translateY(0)` leaves a
   permanent stacking context that traps dropdowns behind later siblings. Entrance
   keyframes must end on `transform: none`.
2. **Don't call a utility class that has no keyframes.** 27 such classes shipped
   dead before this refactor. If you add `animate-*`, define it.

## Client-only preferences

`src/lib/preferences.ts` is a versioned `localStorage` store (accent, density,
panel visibility, saved lanes, intro flag). It must stay backend-free — nothing in
it may enter a search payload.
<!-- END:infreight-design-system -->
