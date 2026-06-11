import asyncio
import os
from datetime import date
from carriers.msc_connector import MSCConnector
from models.schemas import RateSearchRequest

async def test_msc():
    print("Testing MSC Connector...")

    req = RateSearchRequest(
        carriers=["MSC"],
        origin="SGSIN",
        destination="DEHAM",
        service_term="CY/CY",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=18000,
        commodity="Furniture",
        departure_date=str(date.today()),
        search_window_days=14,
    )

    connector = MSCConnector()

    status, quotes = await connector.run_full_search(req)
    print(f"Status: {status}")
    print(f"Extracted {len(quotes)} quote(s)\n")
    
    for i, q in enumerate(quotes):
        print(f"--- Quote {i+1} ---")
        print(f"Vessel: {q.vessel} | Service: {q.service_name}")
        print(f"Routing: {q.routing} | TT: {q.transit_time_days} days")
        print(f"ETD: {q.etd} | ETA: {q.eta}")
        print(f"Total Freight: {q.final_freight_value} {q.currency}")
        print(f"Free Time (Dest): {q.free_time} days")
        print(f"Included Surcharges: {len(q.included_freight_surcharges)}")
        for charge in q.included_freight_surcharges:
            if isinstance(charge, dict):
                print(f"  - {charge['name']}: {charge['amount']} {charge['currency']}")
            else:
                print(f"  - {charge.name}: {charge.amount} {charge.currency}")
        print()

if __name__ == "__main__":
    asyncio.run(test_msc())
