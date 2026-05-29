# -*- coding: utf-8 -*-
"""Hapag-Lloyd end-to-end test -- login + search + extract ALL quotes."""
import os
import asyncio
import json
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

async def test_hapag():
    if not os.getenv("HAPAG_LLOYD_USERNAME"):
        os.environ["HAPAG_LLOYD_USERNAME"] = "BOOKINGSG@IN-FREIGHT.COM"
    if not os.getenv("HAPAG_LLOYD_PASSWORD"):
        os.environ["HAPAG_LLOYD_PASSWORD"] = "IFSGb2020"

    print("Initializing HapagLloydConnector...")
    connector = HapagLloydConnector()

    try:
        print("Logging in...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
        if not login_success:
            return

        request = RateSearchRequest(
            origin="SGSIN",
            destination="DEHAM",
            container_type="DRY 40H",
            container_quantity=2,
            weight_per_container_kg=20000,
            departure_date="tomorrow",
            carriers=["HAPAG_LLOYD"]
        )

        print("Searching quotes...")
        status = await connector.search_quotes(request)
        print(f"Search status: {status}")

        if status.value != "AVAILABLE_QUOTES_FOUND":
            print("No quotes available -- stopping.")
            return

        os.makedirs("scratch", exist_ok=True)
        await connector.page.screenshot(path="scratch/hapag_results_page.png")
        html_content = await connector.page.content()
        with open("scratch/hapag_results_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("Extracting full quote list (all paginated departure dates)...")
        raw_quotes = await connector.extract_quote_list()
        print(f"\nFound {len(raw_quotes)} unique departure dates:")
        for q in raw_quotes:
            print(f"  [{q['seq_idx']}] ETD={q['etd']}  raw='{q['raw_date']}'")

        # -----------------------------------------------------------------------
        # Loop through EVERY quote and extract a price breakdown for each one
        # -----------------------------------------------------------------------
        all_results = []
        failed = []

        print(f"\n{'='*60}")
        print(f"Extracting price breakdowns for all {len(raw_quotes)} quotes...")
        print(f"{'='*60}")

        for q in raw_quotes:
            seq = q["seq_idx"]
            etd = q["etd"]
            print(f"\n[{seq+1}/{len(raw_quotes)}] Processing ETD={etd} ...")

            opened = await connector.open_price_breakdown(q)
            if not opened:
                print(f"  !! Price Breakdown could not be opened for {etd} -- marking sold out / unavailable.")
                q["is_sold_out"] = True
                failed.append(etd)
                continue

            charges = await connector.extract_charge_breakdown()
            if not charges:
                print(f"  !! No charges extracted for {etd}.")
                failed.append(etd)
                continue

            normalized = await connector.normalize_result(q, charges)
            all_results.append(normalized)

            print(f"  ETD:      {normalized.etd}")
            print(f"  ETA:      {normalized.eta}")
            print(f"  Transit:  {normalized.transit_time_days} days")
            print(f"  Service:  {normalized.service_name}")
            print(f"  Total:    USD {normalized.final_freight_value}")
            print(f"  Charges:  {len(normalized.included_freight_surcharges)} line items")

        # -----------------------------------------------------------------------
        # Summary
        # -----------------------------------------------------------------------
        print(f"\n{'='*60}")
        print(f"SUMMARY: {len(all_results)} quotes extracted successfully, {len(failed)} failed.")
        print(f"{'='*60}")
        for r in all_results:
            print(f"  ETD={r.etd}  ETA={r.eta}  Transit={r.transit_time_days}d  Total=USD {r.final_freight_value}  via={r.service_name}")
        if failed:
            print(f"\nFailed/sold-out dates: {failed}")

        # Save full results to JSON
        results_path = "scratch/hapag_all_quotes.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump([json.loads(r.model_dump_json()) for r in all_results], f, indent=2)
        print(f"\nFull results saved to {results_path}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_hapag())
