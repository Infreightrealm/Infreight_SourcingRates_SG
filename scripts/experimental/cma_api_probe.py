#!/usr/bin/env python3
"""
CMA CGM API probe — discovery tool for the experimental API connector.

Runs anywhere with Python 3.8+ and an internet connection. Standard library only:
no pip install, no virtualenv, no backend running, no Chrome. It does not import
anything from this repo and changes nothing in it.

WHY THIS EXISTS
    Before writing a connector we need three facts that only the live gateway can
    tell us:
      1. Which authentication header CMA CGM's gateway expects for this key.
      2. Which API products the key is actually entitled to — a Track & Trace key
         cannot return rates, and that is worth finding out in 30 seconds rather
         than after a day of parser work.
      3. How fast a real rate call is, to compare against the browser connector.

HOW IT DISCOVERS
    On an Azure API Management gateway (which CMA CGM's developer portal is built
    on) the failure modes are usefully distinct:
      - wrong/missing auth header -> 401 "Access denied due to ... subscription key"
      - correct auth, wrong path  -> 404 "Resource not found"
    So a 404 is the signal we want in phase 1: it means the gateway accepted the
    key and only the path was wrong. Phase 2 then walks candidate paths with the
    header that worked.

USAGE
    python3 cma_api_probe.py --key YOUR_KEY
    CMA_CGM_API_KEY=YOUR_KEY python3 cma_api_probe.py

    # once you know the real endpoint from the developer portal:
    python3 cma_api_probe.py --key YOUR_KEY --path /commercial/pricing/v1/spotrates
    python3 cma_api_probe.py --key YOUR_KEY --path /... --time 5

OUTPUT
    A summary table on stdout, plus every raw response body written to
    ./cma_api_probe_out/ for inspection. The key is masked in all output and is
    never written to disk.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TIMEOUT = 20
OUT_DIR = Path("cma_api_probe_out")

# CMA CGM gateway hosts seen in their developer documentation. The probe reports
# which of these resolve and respond; it does not assume any single one is right.
HOSTS = [
    "https://apis.cma-cgm.net",
    "https://apidev.cma-cgm.com",
    "https://api.cma-cgm.com",
]

# Header names commonly used by Azure APIM gateways. Phase 1 finds which one the
# gateway honours for this key.
AUTH_STYLES = [
    ("KeyId", lambda k: {"KeyId": k}),
    ("Ocp-Apim-Subscription-Key", lambda k: {"Ocp-Apim-Subscription-Key": k}),
    ("x-api-key", lambda k: {"x-api-key": k}),
    ("apikey", lambda k: {"apikey": k}),
    ("Authorization: Bearer", lambda k: {"Authorization": f"Bearer {k}"}),
    ("Authorization: apikey", lambda k: {"Authorization": f"apikey {k}"}),
]

# The products this key is actually subscribed to, read from the developer portal
# ("Application 1"). Note what is NOT here: there is no pricing, rates, quotation
# or spot product, so this key cannot return freight rates.
#
# Products are named <domain>.<product>.<version>; the gateway path is the same
# with slashes. Both spellings are probed because the mapping is not documented.
SUBSCRIBED_PRODUCTS = [
    "referential.location.v3",            # port / location lookup — authoritative codes
    "referential.vessel.v1",
    "referential.shipping.company.v1",
    "referential.event.v1",
    "referential.goodscodification.v2",
    "referential.packaging.v2",
    "vesseloperation.commerciallines.v1",  # services / trade lanes
    "vesseloperation.proforma.v2",         # proforma schedules
    "vesseloperation.route.v2",            # routings
    "vesseloperation.voyage.v2",           # voyages, ETD/ETA
    "operation.trackandtrace.v1",          # post-booking tracking
]


def product_paths(product: str) -> list[str]:
    """Candidate gateway paths for a portal product name."""
    slashed = "/" + product.replace(".", "/")
    return [slashed, f"/{product}"]


CANDIDATE_PATHS = [p for prod in SUBSCRIBED_PRODUCTS for p in product_paths(prod)]

# The cheapest product to use as a canary: a location lookup is small, read-only
# and certainly subscribed, so one call confirms both host and auth header.
CANARY_PRODUCT = "referential.location.v3"


def mask(key: str) -> str:
    if not key:
        return "(empty)"
    if len(key) <= 10:
        return key[:2] + "…" + key[-2:]
    return f"{key[:4]}…{key[-4:]} ({len(key)} chars)"


class BudgetExhausted(Exception):
    """Raised when the probe has spent its allowance of the hourly API quota."""


_spent = 0
_budget = 15


def set_budget(n: int) -> None:
    global _budget
    _budget = n


def spent() -> int:
    return _spent


def request(url: str, headers: dict, method: str = "GET", body: bytes | None = None):
    """Return (status, reason, body_text, elapsed_ms). Never raises for HTTP errors."""
    global _spent
    if _spent >= _budget:
        raise BudgetExhausted(f"stopped after {_spent} requests to stay inside the hourly quota")
    _spent += 1
    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "infreight-api-probe/1.0")
    ctx = ssl.create_default_context()
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            text = resp.read().decode("utf-8", "replace")
            return resp.status, resp.reason, text, (time.perf_counter() - started) * 1000
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, e.reason, text, (time.perf_counter() - started) * 1000
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}", "", (time.perf_counter() - started) * 1000
    except Exception as e:  # socket timeouts, TLS failures, DNS
        return 0, f"{type(e).__name__}: {e}", "", (time.perf_counter() - started) * 1000


def verdict(status: int, body: str) -> str:
    """Translate a response into what it tells us about auth vs path."""
    low = body.lower()
    if status == 0:
        return "unreachable"
    if status in (401, 403):
        if "subscription key" in low or "access denied" in low:
            return "auth-rejected"
        return "auth-rejected?"
    if status == 404:
        # Auth passed the gateway; only the operation was wrong.
        return "AUTH OK (path wrong)"
    if 200 <= status < 300:
        return "SUCCESS"
    if status == 400:
        # Reached a real operation and it validated our (empty) input.
        return "AUTH OK (endpoint real, needs params)"
    if status in (405, 415):
        return "AUTH OK (wrong method/content-type)"
    if status == 429:
        return "rate-limited"
    return f"http {status}"


def save(name: str, content: str) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in name)[:120]
    (OUT_DIR / f"{safe}.txt").write_text(content, encoding="utf-8")


def snippet(body: str, n: int = 160) -> str:
    one_line = " ".join(body.split())
    return one_line[:n] + ("…" if len(one_line) > n else "")


def phase1_auth(key: str, hosts: list[str]) -> list[tuple[str, str]]:
    """Find (host, auth style) pairs the gateway accepts. Returns winners."""
    print("\n" + "=" * 78)
    print("PHASE 1 — which host + auth header does this key work with?")
    print("=" * 78)
    print("Probing a product the key is subscribed to, so a 200 confirms host and")
    print("header at once. A 404 also means the key was accepted and only the path")
    print("was wrong. A 401 means the header name or key is wrong.")
    print("Stops at the first working combination — the hourly quota is small.\n")

    probe_path = product_paths(CANARY_PRODUCT)[0]
    winners: list[tuple[str, str]] = []

    for host in hosts:
        print(f"\n  {host}   (probing {probe_path})")
        reachable = False
        for label, build in AUTH_STYLES:
            try:
                status, reason, body, ms = request(host + probe_path, build(key))
            except BudgetExhausted as e:
                print(f"    -- {e}")
                return winners
            v = verdict(status, body)
            if status != 0:
                reachable = True
            hit = v.startswith("AUTH OK") or v == "SUCCESS"
            print(f"    {label:<30} {status or '---':>4}  {v:<32} {ms:6.0f}ms{'  <<<' if hit else ''}")
            save(f"phase1_{host}_{label}", f"{status} {reason}\n\n{body}")
            if hit:
                winners.append((host, label))
                print("    -> accepted; skipping the remaining headers to save quota.")
                return winners
        if not reachable:
            print("    (host did not respond at all — DNS, firewall, or wrong hostname)")

    return winners


def phase2_paths(key: str, host: str, auth_label: str, paths: list[str]) -> list[str]:
    """With a working auth header, find which product paths exist."""
    build = dict(AUTH_STYLES)[auth_label]
    print("\n" + "=" * 78)
    print(f"PHASE 2 — which endpoints exist on {host}")
    print(f"           using auth header: {auth_label}")
    print("=" * 78 + "\n")

    live: list[str] = []
    for path in paths:
        try:
            status, reason, body, ms = request(host + path, build(key))
        except BudgetExhausted as e:
            print(f"\n  -- {e}")
            print("     Re-run with --budget N (quota permitting) to continue.")
            break
        v = verdict(status, body)
        interesting = v == "SUCCESS" or "endpoint real" in v or v.startswith("AUTH OK (wrong")
        flag = "  <<<" if interesting else ""
        print(f"  {path:<48} {status or '---':>4}  {v:<34} {ms:6.0f}ms{flag}")
        save(f"phase2_{path}", f"{status} {reason}\n\n{body}")
        if interesting:
            live.append(path)
        if status in (200, 400) and body:
            print(f"       -> {snippet(body)}")
    return live


def phase3_timing(key: str, host: str, auth_label: str, path: str, runs: int) -> None:
    """Time repeated calls so the result can be compared against the scraper."""
    build = dict(AUTH_STYLES)[auth_label]
    print("\n" + "=" * 78)
    print(f"PHASE 3 — timing {runs} calls to {path}")
    print("=" * 78 + "\n")

    times = []
    for i in range(runs):
        status, reason, body, ms = request(host + path, build(key))
        times.append(ms)
        print(f"  run {i + 1}: {status} in {ms:.0f}ms")
    if times:
        times_sorted = sorted(times)
        median = times_sorted[len(times_sorted) // 2]
        print(f"\n  fastest {min(times):.0f}ms | median {median:.0f}ms | slowest {max(times):.0f}ms")
        print("\n  For comparison, the browser connector takes roughly 60–180 seconds")
        print("  per port pair. Anything here under ~5s is a decisive win.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe the CMA CGM API to discover what a key can do.")
    ap.add_argument("--key", default=os.getenv("CMA_CGM_API_KEY", ""),
                    help="API key. Defaults to $CMA_CGM_API_KEY.")
    ap.add_argument("--host", help="Skip host discovery and use only this host.")
    ap.add_argument("--auth", help="Skip auth discovery and use this header name (see AUTH_STYLES).")
    ap.add_argument("--path", action="append",
                    help="Test this exact path instead of the candidate list. Repeatable.")
    ap.add_argument("--time", type=int, default=0, metavar="N",
                    help="After discovery, time N calls against the first working path.")
    ap.add_argument("--budget", type=int, default=15, metavar="N",
                    help="Maximum requests to spend. The portal quota is 20/hour, "
                         "so the default leaves headroom. (default: 15)")
    args = ap.parse_args()
    set_budget(args.budget)

    if not args.key:
        print("No key given. Pass --key YOUR_KEY or set CMA_CGM_API_KEY.", file=sys.stderr)
        return 2

    print("CMA CGM API probe")
    print(f"key: {mask(args.key)}")
    print(f"raw responses will be written to: {OUT_DIR.resolve()}")

    hosts = [args.host] if args.host else HOSTS

    known_auth = dict(AUTH_STYLES)
    if args.auth and args.auth not in known_auth:
        print(f"\nUnknown --auth '{args.auth}'. Choose one of:", file=sys.stderr)
        for label, _ in AUTH_STYLES:
            print(f"  {label}", file=sys.stderr)
        return 2

    if args.auth and args.host:
        winners = [(args.host, args.auth)]
        print("\n(skipping phase 1 — host and auth supplied)")
    else:
        winners = phase1_auth(args.key, hosts)

    if not winners:
        print("\n" + "=" * 78)
        print("RESULT: no host/header combination accepted this key.")
        print("=" * 78)
        print("""
This usually means one of:
  - the key needs to be subscribed to a specific API product in the CMA CGM
    developer portal before it works (most common),
  - the key is an OAuth client-id that must first be exchanged for a bearer
    token at a /token endpoint, rather than a direct API key,
  - the gateway hostname is different for your account.

Check the developer portal for the exact base URL and the sample curl it shows
for your product, then re-run with --host and --path.""")
        return 1

    host, auth_label = winners[0]
    print("\n" + "=" * 78)
    print(f"RESULT: key accepted by {host} using header '{auth_label}'")
    print("=" * 78)

    paths = args.path if args.path else CANDIDATE_PATHS
    live = phase2_paths(args.key, host, auth_label, paths)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  working host   : {host}")
    print(f"  working header : {auth_label}")
    if live:
        print(f"  live endpoints : {len(live)}")
        for p in live:
            print(f"      {p}")
        pricing = [p for p in live if any(w in p for w in ("pric", "rate", "quot", "spot"))]
        if pricing:
            print("\n  A PRICING endpoint responded — an API rate connector is viable.")
        else:
            print("\n  No pricing endpoint responded, which matches the portal: this")
            print("  application is subscribed to referential, vesseloperation and")
            print("  trackandtrace products only. None of those return freight rates,")
            print("  so the browser connector stays the only source of CMA CGM prices.")
            print("  What these ARE good for: authoritative port/location lookup and")
            print("  schedule data. See scripts/experimental/README.md.")
    else:
        print("  live endpoints : none of the candidates matched")
        print("\n  The key works but none of the guessed paths were right. Get the exact")
        print("  path from the developer portal and re-run with --path /that/path.")

    if args.time and live:
        phase3_timing(args.key, host, auth_label, live[0], args.time)

    print(f"\nRaw response bodies saved in {OUT_DIR.resolve()}")
    print("Send the output above (or that folder) back and the connector's parser")
    print("can be written against the real response shape.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
