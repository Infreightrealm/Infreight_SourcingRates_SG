"""
Live search verification script for port logging and mismatch detection.
Executes a live search for ambiguous input 'PK' -> 'JKT' against Maersk connector,
and prints the exact database record stored in CarrierSearchResult.
"""
import sys
import os
import asyncio
from uuid import uuid4
from sqlalchemy import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.database import get_async_session_maker, init_db
from models.rate_search import RateSearch, CarrierSearchResult
from models.schemas import RateSearchRequest
from services.job_service import run_carrier_search


async def run_live_verification():
    print("=== STARTING LIVE PORT LOGGING VERIFICATION ===")
    await init_db()

    search_id = uuid4()
    origin_input = "Singapore"
    dest_input = "Jakarta"
    carrier_code = "MAERSK"


    # Step 1: Create DB records
    async with get_async_session_maker()() as session:
        rs = RateSearch(
            id=search_id,
            origin=origin_input,
            destination=dest_input,
            container_type="DRY 40H",
            container_quantity=1,
            commodity="General Cargo",
            departure_date="tomorrow",
            selected_carriers=[carrier_code],
            status="QUEUED"
        )
        csr = CarrierSearchResult(
            search_id=search_id,
            carrier=carrier_code,
            status="QUEUED"
        )
        session.add(rs)
        session.add(csr)
        await session.commit()

    # Step 2: Execute live carrier search
    req = RateSearchRequest(
        origin=origin_input,
        destination=dest_input,
        container_type="DRY 40H",
        container_quantity=1,
        commodity="General Cargo",
        departure_date="tomorrow",
        carriers=[carrier_code],
        use_mock=False
    )

    print(f"Running live search: Origin='{origin_input}' -> Destination='{dest_input}' on {carrier_code}...")

    await run_carrier_search(search_id, carrier_code, req)

    # Step 3: Read back persisted CarrierSearchResult DB record
    async with get_async_session_maker()() as session:
        res = (await session.execute(
            select(CarrierSearchResult).where(CarrierSearchResult.search_id == search_id)
        )).scalar_one()

        print("\n=======================================================")
        print("    ACTUAL LOGGED DATABASE RECORD (CarrierSearchResult)  ")
        print("=======================================================")
        print(f"CarrierSearchResult ID  : {res.id}")
        print(f"Search ID               : {res.search_id}")
        print(f"Carrier Code            : {res.carrier}")
        print(f"Outcome Status          : {res.status}")
        print(f"Error Message           : {res.error_message}")
        print("-------------------------------------------------------")
        print(f"Raw Origin Input        : '{res.raw_origin_input}'")
        print(f"Raw Destination Input   : '{res.raw_destination_input}'")
        print(f"Resolved Origin Name    : '{res.resolved_origin_name}'")
        print(f"Resolved Origin LOCODE  : '{res.resolved_origin_locode}'")
        print(f"Resolved Dest Name      : '{res.resolved_destination_name}'")
        print(f"Resolved Dest LOCODE    : '{res.resolved_destination_locode}'")
        print("-------------------------------------------------------")
        print(f"Submitted Origin        : '{res.submitted_origin}'")
        print(f"Submitted Destination   : '{res.submitted_destination}'")
        print(f"Matched Origin (Page)   : '{res.matched_origin}'")
        print(f"Matched Destination     : '{res.matched_destination}'")
        print("-------------------------------------------------------")
        print(f"Has Port Mismatch       : {res.has_port_mismatch}")
        print(f"Mismatch Warning        : {res.mismatch_warning}")
        print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(run_live_verification())
