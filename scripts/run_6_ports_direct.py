# -*- coding: utf-8 -*-
import sys
import os
import asyncio
from datetime import date, timedelta

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from models.schemas import RateSearchRequest, CarrierResultStatus
from carriers.registry import get_connector

ORIGIN = "Pasir Gudang, Malaysia"
PORTS = [
    "AHMEDABAD",
    "ALEXANDRIA",
    "AL-SOKHNA",
    "ALTAMIRA",
    "AMBARLI",
    "ANTWERP"
]
CARRIERS = ["ONE", "CMA_CGM"]

async def run_carrier(carrier_code):
    connector = get_connector(carrier_code)
    if not connector:
        print(f"[{carrier_code}] Connector not found", flush=True)
        return []

    print(f"[{carrier_code}] Starting Persistent Session for 6 Ports...", flush=True)
    requests = []
    for dest in PORTS:
        req = RateSearchRequest(
            carriers=[carrier_code],
            origin=ORIGIN,
            destination=dest,
            service_term="CY/CY",
            container_types=["DRY 20", "DRY 40"],
            departure_date="tomorrow",
            search_window_days=14,
            search_mode="quick"
        )
        requests.append(req)

    async def callback(idx, req, status, quotes):
        print(f"[{carrier_code}] Route {idx+1}/6 ({req.destination}): {status}", flush=True)
        for q in quotes:
            print(f"  -> Container: {q.container_type} | Final Price: ${q.final_freight_value} {q.currency}", flush=True)

    results = await connector.run_batch_persistent_search(requests, route_callback=callback)
    return results

async def main():
    print("================================================================", flush=True)
    print(" [ULTRA-FAST QUICK SEARCH] PASIR GUDANG -> 6 PORTS", flush=True)
    print(" Carriers: ONE, CMA CGM | Mode: Final Freight Price Only", flush=True)
    print("================================================================\n", flush=True)

    tasks = [run_carrier(c) for c in CARRIERS]
    all_res = await asyncio.gather(*tasks, return_exceptions=True)

    print("\n================================================================", flush=True)
    print(" [FINAL 6-PORT RATE MATRIX]", flush=True)
    print("================================================================", flush=True)

    matrix = {}
    for dest in PORTS:
        matrix[dest] = {}

    for c_code, res in zip(CARRIERS, all_res):
        if isinstance(res, Exception):
            print(f"[{c_code}] Error: {res}", flush=True)
            continue
        for req, status, quotes in res:
            q20 = next((q for q in quotes if "20" in (q.container_type or "")), None)
            q40 = next((q for q in quotes if "40" in (q.container_type or "")), None)
            matrix[req.destination][c_code] = {
                "20": q20.final_freight_value if q20 else "-",
                "40": q40.final_freight_value if q40 else "-",
                "status": status.value if hasattr(status, "value") else str(status)
            }

    print(f"\n{'PORT DESTINATION':<20} | {'ONE 20GP':<12} | {'ONE 40GP':<12} | {'CMA 20GP':<12} | {'CMA 40GP':<12}", flush=True)
    print("-" * 80, flush=True)
    for dest in PORTS:
        one_data = matrix[dest].get("ONE", {})
        cma_data = matrix[dest].get("CMA_CGM", {})
        one_20 = f"${one_data.get('20')}" if isinstance(one_data.get('20'), (int, float)) else str(one_data.get('20', '-'))
        one_40 = f"${one_data.get('40')}" if isinstance(one_data.get('40'), (int, float)) else str(one_data.get('40', '-'))
        cma_20 = f"${cma_data.get('20')}" if isinstance(cma_data.get('20'), (int, float)) else str(cma_data.get('20', '-'))
        cma_40 = f"${cma_data.get('40')}" if isinstance(cma_data.get('40'), (int, float)) else str(cma_data.get('40', '-'))
        print(f"{dest:<20} | {one_20:<12} | {one_40:<12} | {cma_20:<12} | {cma_40:<12}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
