#!/usr/bin/env python3
"""
CMA CGM SpotOn — live test. Run this to find out whether the API beats the crawler.

Standard library only: no pip install, no virtualenv, no backend running, no
Chrome. Runs on any machine with Python 3.8+ and internet. It imports nothing
from this repo and changes nothing in it.

WHAT IT DOES
    1. Exchanges your client id/secret for an OAuth2 token
       (https://auth.cma-cgm.com/as/token.oauth2, scope instantquote:read:be).
    2. Posts one search to /spotOn/search covering every container size at once.
    3. Prints what came back, readably, and times it.
    4. Saves the raw JSON so the connector's parser can be checked against it.

QUOTA
    The portal allows 20 requests/hour. One run of this script costs 2 (a token
    and a search). It refuses to make more than --max-requests calls.

USAGE
    python3 cma_spoton_test.py --client-id XXX --client-secret YYY
    python3 cma_spoton_test.py --client-id XXX --client-secret YYY \
        --pol SGSIN --pod DEHAM --sizes 20GP,40GP,40HC --date 2026-10-05

    Credentials can also come from CMA_CGM_API_CLIENT_ID / _CLIENT_SECRET.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

TOKEN_URL = "https://auth.cma-cgm.com/as/token.oauth2"
BASE_URL = "https://apis.cma-cgm.net/pricing/commercial/instantquote/v2"
SEARCH_PATH = "/spotOn/search"
SCOPE = "instantquote:read:be"
OUT_DIR = Path("cma_spoton_out")

# Sentinels the spec puts in offerId when there is no priced offer.
NO_OFFER = {"no-offer", "sold-out", "quantities cannot be confirmed",
            "offer cannot be created under fmc scope"}

_calls = 0
_max_calls = 4


def _http(url: str, *, data: bytes | None, headers: dict, method: str):
    """Return (status, body_text, elapsed_ms). Never raises for HTTP errors."""
    global _calls
    if _calls >= _max_calls:
        print(f"\nStopping: would exceed --max-requests ({_max_calls}).")
        sys.exit(1)
    _calls += 1

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=90, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace"), (time.perf_counter() - started) * 1000
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, body, (time.perf_counter() - started) * 1000
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}", (time.perf_counter() - started) * 1000


def get_token(client_id: str, client_secret: str) -> str | None:
    print("1. Requesting OAuth2 token …")
    form = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": SCOPE,
    }).encode()
    status, body, ms = _http(
        TOKEN_URL, data=form, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"})

    if status != 200:
        print(f"   FAILED — HTTP {status} in {ms:.0f}ms")
        print(f"   {body[:500]}")
        if status in (400, 401):
            print("\n   A 400/401 here means the client id or secret is wrong, or this")
            print("   client is not authorised for the instantquote:read:be scope.")
        return None

    try:
        token = json.loads(body).get("access_token")
    except json.JSONDecodeError:
        print(f"   FAILED — token endpoint did not return JSON: {body[:200]}")
        return None

    if not token:
        print(f"   FAILED — no access_token in response: {body[:200]}")
        return None
    print(f"   OK — token received in {ms:.0f}ms")
    return token


def search(token: str, pol: str, pod: str, sizes: list[str], qty: int,
           weight: float, dep: str, behalf_of: str | None):
    payload = {
        "departureDate": dep,
        "locationCodificationType": "UNLOCODE",
        "portOfLoading": pol,
        "portOfDischarge": pod,
        "commodityCode": "FAK",
        "spotDDSMConditionsOnly": True,
        "requestedEquipments": [
            {"equipmentGroupIsoCode": s, "numberOfContainers": qty,
             "weightPerContainer": weight} for s in sizes
        ],
    }
    url = BASE_URL + SEARCH_PATH
    if behalf_of:
        url += "?" + urllib.parse.urlencode({"behalfOf": behalf_of})

    print(f"\n2. POST {SEARCH_PATH}")
    print(f"   {pol} -> {pod}, {'+'.join(sizes)}, {qty}x{weight:.0f}kg, departing {dep}")
    status, body, ms = _http(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 "Accept": "application/json",
                 "range": "0-4"})
    print(f"   HTTP {status} in {ms:.0f}ms")

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "request.json").write_text(json.dumps(payload, indent=2))
    (OUT_DIR / "response.json").write_text(body)
    return status, body, ms


def describe(body: str) -> None:
    """Print the offers in a form a person can check against the portal."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"   Response was not JSON:\n   {body[:400]}")
        return

    items = data if isinstance(data, list) else [data]
    offers = [i for i in items if isinstance(i, dict) and "offerId" in i]
    messages = [i for i in items if isinstance(i, dict) and "offerId" not in i and i.get("code")]

    print(f"\n3. {len(offers)} offer(s), {len(messages)} message(s)")

    for m in messages:
        print(f"   ! {m.get('code')}: {m.get('description')}")

    for o in offers:
        oid = str(o.get("offerId", ""))
        etd = str(o.get("departureDate", ""))[:10]
        eta = str(o.get("arrivalDate", ""))[:10]
        transit = o.get("transitTime")
        legs = o.get("routingLegs") or []
        vessel = legs[0].get("vesselName") if legs else None
        service = ((legs[0].get("service") or {}).get("name")) if legs else None

        if oid.lower() in NO_OFFER:
            print(f"\n   {etd}  {oid}  (no price)")
            continue

        print(f"\n   {etd} -> {eta}  transit {transit}d  {vessel or '?'}  [{service or '?'}]")
        ql = o.get("quoteLine") or {}
        print(f"     validity {ql.get('validityFrom','?')} to {ql.get('validityTo','?')}")

        per_eq = ((ql.get("surcharges") or {}).get("matchingSurchargesPerEquipmentTypes")) or []
        for eq in per_eq:
            cur = ((eq.get("currency") or {}).get("code")) or ""
            print(f"     {eq.get('equipmentGroupIsoCode'):<6} "
                  f"ocean {eq.get('basicOceanFreightRate')} "
                  f"all-in {eq.get('allInRate')} {cur}")
            for s in eq.get("matchingCargoSurcharges") or []:
                ch = s.get("charge") or {}
                inc = " (already in ocean freight)" if s.get("includedInBasicFreight") else ""
                print(f"        + {ch.get('name') or ch.get('code')}: {s.get('amount')}{inc}")

        for cond in o.get("ddsmConditions") or []:
            t = (cond.get("tariff") or {})
            for by_eq in cond.get("conditionsByEquipment") or []:
                fd = by_eq.get("freeDays") or {}
                if fd.get("number") is not None:
                    print(f"     {t.get('name','?')}: {fd['number']} "
                          f"{fd.get('calculationType','')} free days "
                          f"({by_eq.get('equipmentGroupIsoCode')})")


def main() -> int:
    global _max_calls
    today = date.today()
    ap = argparse.ArgumentParser(description="Live test of the CMA CGM SpotOn API.")
    ap.add_argument("--client-id", default=os.getenv("CMA_CGM_API_CLIENT_ID", ""))
    ap.add_argument("--client-secret", default=os.getenv("CMA_CGM_API_CLIENT_SECRET", ""))
    ap.add_argument("--pol", default="SGSIN", help="Port of loading UN/LOCODE")
    ap.add_argument("--pod", default="DEHAM", help="Port of discharge UN/LOCODE")
    ap.add_argument("--sizes", default="20GP,40GP,40HC",
                    help="Equipment ISO codes, comma separated")
    ap.add_argument("--qty", type=int, default=1)
    ap.add_argument("--weight", type=float, default=20000)
    ap.add_argument("--date", default=(today + timedelta(days=7)).isoformat(),
                    help="Departure date YYYY-MM-DD (must be today..today+30)")
    ap.add_argument("--behalf-of", default=os.getenv("CMA_CGM_API_BEHALF_OF", "") or None,
                    help="End customer code; required only for third parties")
    ap.add_argument("--max-requests", type=int, default=4,
                    help="Hard cap on API calls. Quota is 20/hour. (default: 4)")
    args = ap.parse_args()
    _max_calls = args.max_requests

    if not args.client_id or not args.client_secret:
        print("Need --client-id and --client-secret (or CMA_CGM_API_CLIENT_ID / "
              "CMA_CGM_API_CLIENT_SECRET).", file=sys.stderr)
        return 2

    # Guard the documented DAT_ERR window rather than spending a call to learn it.
    if not (today.isoformat() <= args.date <= (today + timedelta(days=30)).isoformat()):
        print(f"Departure date must be between {today} and {today + timedelta(days=30)} "
              f"(the API returns DAT_ERR otherwise).", file=sys.stderr)
        return 2

    print("CMA CGM SpotOn live test")
    print(f"quota note: this run costs 2 of your 20 requests/hour\n")

    token = get_token(args.client_id, args.client_secret)
    if not token:
        return 1

    sizes = [s.strip() for s in args.sizes.split(",") if s.strip()]
    status, body, ms = search(token, args.pol, args.pod, sizes, args.qty,
                              args.weight, args.date, args.behalf_of)

    if status in (200, 206):
        describe(body)
        print("\n" + "=" * 70)
        print(f"SUCCESS — priced in {ms:.0f}ms ({ms / 1000:.1f}s)")
        print("=" * 70)
        print("The browser connector takes roughly 60-180 seconds for the same")
        print(f"work, so this is on the order of {max(60000 / ms, 1):.0f}x faster.")
        if status == 206:
            print("\nHTTP 206 Partial Content: some sizes or quantities were adjusted.")
    else:
        print("\n" + "=" * 70)
        print(f"FAILED — HTTP {status}")
        print("=" * 70)
        print(body[:800])
        if status == 400:
            print("\nThe spec maps 400 codes to causes: POR_ERR unknown port, "
                  "EQP_ERR unknown equipment,\nDAT_ERR bad date, PTC_ERR missing "
                  "origin/destination, CDY_ERR bad commodity,\nMKP_ERR behalfOf "
                  "required for market places.")
        elif status == 403:
            print("\n403 IRT_ERR: the token is valid but lacks rights for this "
                  "operation.\nCheck the client is subscribed to SpotOn with "
                  "instantquote:read:be.")

    print(f"\nRaw request and response saved in {OUT_DIR.resolve()}")
    print(f"API calls used this run: {_calls}")
    return 0 if status in (200, 206) else 1


if __name__ == "__main__":
    sys.exit(main())
