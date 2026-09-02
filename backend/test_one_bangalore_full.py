import asyncio
import os
import sys
from datetime import date, timedelta

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest, CarrierResultStatus

# Ensure live mode
os.environ["USE_MOCK_CARRIERS"] = "false"
os.environ["ONE_DEBUG"] = "true"

async def test_live_one_bangalore():
    print("=" * 70)
    print("  RUNNING LIVE TEST: ONE CONNECTOR (SINGAPORE -> BANGALORE)")
    print("=" * 70)

    connector = ONEConnector()
    
    # Departure date: next Saturday (Aug 22, 2026 or +4 days)
    dep_date = (date.today() + timedelta(days=4)).isoformat()
    
    req = RateSearchRequest(
        carriers=["ONE"],
        origin="Singapore",
        destination="INBLR",
        service_term="CY/CY",
        container_type="DRY 20",
        container_types=["DRY 20", "DRY 40", "DRY 40H"],
        container_quantity=1,
        weight_per_container_kg=20000.0,
        commodity="General",
        departure_date=dep_date,
        search_window_days=14
    )

    try:
        status, quotes = await connector.run_full_search(req)
        print("\n" + "=" * 70)
        print(f"SEARCH RESULT STATUS: {status}")
        print(f"TOTAL QUOTES RETURNED: {len(quotes)}")
        print("=" * 70)

        for idx, q in enumerate(quotes):
            print(f"\n--- Quote #{idx + 1} ---")
            print(f"  Container Type:       {q.container_type}")
            print(f"  Vessel / Service:     {q.vessel} ({q.service_name})")
            print(f"  ETD POL -> ETA POD:   {q.etd} -> {q.eta} ({q.transit_time_days} days)")
            print(f"  Routing:              {q.routing}")
            print(f"  Basic Ocean Freight:  ${q.basic_ocean_freight} {q.currency}")
            print(f"  Discount:             ${q.discount} {q.currency}")
            print(f"  Freight Surcharges:   {len(q.included_freight_surcharges)} item(s)")
            for s in q.included_freight_surcharges:
                print(f"    + {s.name}: {s.amount} {s.currency}")
            print(f"  Excluded Charges:     {len(q.excluded_charges)} item(s)")
            for e in q.excluded_charges:
                print(f"    - [{e.category}] {e.name}: {e.amount} {e.currency}")
            print(f"  ---> FINAL FREIGHT VALUE: ${q.final_freight_value} {q.currency}")

    except Exception as err:
        print(f"\n[TEST ERROR] Live search failed: {err}")
        import traceback
        traceback.print_exc()
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_live_one_bangalore())
