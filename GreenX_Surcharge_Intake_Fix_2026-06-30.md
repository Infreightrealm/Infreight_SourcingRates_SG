# GreenX — Surcharge Intake Fix (2026-06-30)

**Component:** `backend/carriers/greenx_connector.py` → `_split_raw_quote_by_container_types`
**Commit:** `45d2481`
**Status:** ✅ Implemented, verified, and pushed to `main`.

---

## Problem

GreenX quotes only folded **Basic Ocean Freight** and **LOW SULPHUR SURCHARGE (LSS)**
into the final freight value. The other mandatory charges were missing from the
per-container totals.

### Charges that must be taken into the final value (USD only)
- Basic Ocean Freight
- EU INNOVATION SURCHARGE (EUIS)
- IMO SOX COMPLIANCE CHARGE (ISOCC)
- LOW SULPHUR SURCHARGE (LSS)

### Per-B/L charges (billed once per booking, added in full to *each* container type)
- EU ENTRY SUMMARY DECLARATION CHARGE (ENS)
- E BOOKING FEE VIA GREENX (EBKF)

Example: a $10 ENS adds $10 to the final total of **each** of DRY 20 / DRY 40 / DRY 40H.

---

## Root cause

In `_split_raw_quote_by_container_types`, incoming charges are separated into
**container-specific** charges and **flat / per-B/L** charges. The surcharge
whitelist (`INCLUDED_SURCHARGES`) was only applied to the **flat** charges:

```python
# container-specific charges — OLD
"category": "BASIC_OCEAN_FREIGHT" if name == "BASIC OCEAN FREIGHT" else "ORIGIN_CHARGE_EXCLUDED"
```

Any container-specific charge that was not Basic Ocean Freight was hardcoded to
`ORIGIN_CHARGE_EXCLUDED`. GreenX bills **EUIS** and **ISOCC** (and often **LSS**)
**per container**, so they landed in the container bucket and were always dropped.
Only the per-B/L LSS line — which went through the flat path where the whitelist
*was* applied — survived. That is why the output showed only BOF + LSS.

---

## Fix

Introduced a single classifier used for **both** container-specific and per-B/L
charges, which also enforces a **USD-only** rule:

```python
INCLUDED_SURCHARGES = {
    "EU INNOVATION SURCHARGE (EUIS)",
    "IMO SOX COMPLIANCE CHARGE (ISOCC)",
    "LOW SULPHUR SURCHARGE (LSS)",
    "EU ENTRY SUMMARY DECLARATION CHARGE (ENS)",
    "E BOOKING FEE VIA GREENX (EBKF)",
}

def _categorize(name, currency):
    name_u = " ".join((name or "").upper().split())   # whitespace-normalized
    if name_u == "BASIC OCEAN FREIGHT":
        return "BASIC_OCEAN_FREIGHT"
    if name_u in INCLUDED_SURCHARGES and (currency or "").upper() == "USD":
        return "FREIGHT_SURCHARGE_INCLUDED"
    return "ORIGIN_CHARGE_EXCLUDED"
```

- Applied to **container-specific** charges → EUIS / ISOCC / LSS are now included.
- Applied to **per-B/L** charges → ENS / EBKF are included and, because the flat
  charges are appended to every container size, each size gets their full amount.
- **USD-only guard:** a charge is folded in only when billed in USD; a whitelisted
  charge in another currency (e.g. EUR) is excluded.
- Name matching is whitespace-normalized to tolerate scraped spacing differences.

Final value per container type = `Basic Ocean Freight + Σ(included surcharges)`.

---

## Verification

Ran an isolated test of `_split_raw_quote_by_container_types` with per-container
BOF/EUIS/ISOCC/LSS, per-B/L ENS ($10) / EBKF ($5), a non-USD EUIS (EUR), and a
non-whitelisted Terminal Handling charge:

| Container | Final value | Breakdown |
|-----------|-------------|-----------|
| DRY 20  | **1095.00** | 1000 + 25 + 15 + 40 + 10 + 5 |
| DRY 40  | **1925.00** | 1800 + 30 + 20 + 60 + 10 + 5 |
| DRY 40H | **2025.00** | 1900 + 30 + 20 + 60 + 10 + 5 |

- All five surcharges appear under `included_freight_surcharges` for every size.
- The **EUR** EUIS line and the **Terminal Handling** charge are correctly excluded.

---

## Files changed
- `backend/carriers/greenx_connector.py` — `_split_raw_quote_by_container_types`
- `CHANGELOG.md` — `[2026-06-30]` entry
