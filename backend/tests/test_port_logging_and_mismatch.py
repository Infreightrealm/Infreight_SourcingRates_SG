"""
Unit tests for Port Search Reliability Logging and Mismatch Detection.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy import select

from services.job_service import _detect_port_mismatch, run_carrier_search
from models.database import get_async_session_maker, init_db
from models.rate_search import RateSearch, CarrierSearchResult
from models.schemas import RateSearchRequest, CarrierResultStatus


def test_detect_port_mismatch_verified_match():
    """Test that matching LOCODE or City + Country code returns False (Verified Match)."""
    # 1. LOCODE match
    assert _detect_port_mismatch("Singapore", "SGSIN", "Singapore, Singapore (SGSIN)") is False
    
    # 2. City + Country match (Port Klang / Port Kelang, MY)
    assert _detect_port_mismatch("Port Klang", "MYPKG", "Port Kelang, MY") is False
    assert _detect_port_mismatch("Hamburg", "DEHAM", "Hamburg, Germany (DEHAM)") is False
    assert _detect_port_mismatch("Pasir Gudang, Johor", "MYPGU", "Pasir Gudang (Johor), Malaysia") is False



def test_detect_port_mismatch_verified_mismatch():
    """Test that differing port strings return True (Verified Mismatch)."""
    # Different country
    assert _detect_port_mismatch("Singapore", "SGSIN", "Subic Bay, Philippines (PHSBC)") is True
    
    # Different city in same country
    assert _detect_port_mismatch("Port Klang", "MYPKG", "Penang, Malaysia (MYPEN)") is True


def test_detect_port_mismatch_unknown_null():
    """Test that null/empty matched port strings return None (Unknown / Could Not Verify)."""
    assert _detect_port_mismatch("Singapore", "SGSIN", None) is None
    assert _detect_port_mismatch("Singapore", "SGSIN", "") is None
    assert _detect_port_mismatch("Singapore", "SGSIN", "   ") is None


@pytest.mark.asyncio
async def test_job_service_port_logging_persistence():
    """Test that run_carrier_search persists all port observability fields to DB."""
    await init_db()
    
    search_id = uuid4()
    async with get_async_session_maker()() as session:
        rs = RateSearch(
            id=search_id,
            origin="Singapore",
            destination="Hamburg",
            container_type="DRY 40H",
            container_quantity=1,
            commodity="General Cargo",
            departure_date="2026-08-15",
            selected_carriers=["MAERSK"],
            status="QUEUED"
        )
        csr = CarrierSearchResult(
            search_id=search_id,
            carrier="MAERSK",
            status="QUEUED"
        )
        session.add(rs)
        session.add(csr)
        await session.commit()

    # Run mock carrier search outside active session block
    os.environ["USE_MOCK_CARRIERS"] = "true"
    req = RateSearchRequest(
        origin="Singapore",
        destination="Hamburg",
        container_type="DRY 40H",
        container_quantity=1,
        commodity="General Cargo",
        departure_date="2026-08-15",
        carriers=["MAERSK"],
        use_mock=True
    )
    await run_carrier_search(search_id, "MAERSK", req)


    # Retrieve saved record in fresh session
    async with get_async_session_maker()() as session:
        res = (await session.execute(
            select(CarrierSearchResult).where(CarrierSearchResult.search_id == search_id)
        )).scalar_one()

        assert res.raw_origin_input == "Singapore"
        assert res.raw_destination_input == "Hamburg"
        assert res.resolved_origin_locode == "SGSIN"
        assert res.resolved_destination_locode == "DEHAM"
        assert res.submitted_origin == "Singapore"
        assert res.submitted_destination == "Hamburg"
        assert res.matched_origin == "Singapore"
        assert res.matched_destination == "Hamburg"
        assert res.has_port_mismatch is False
        assert res.mismatch_warning is None

@pytest.mark.asyncio
async def test_admin_route_health_endpoint():
    """Test that /api/admin/route-health endpoint returns formatted route health matrix."""
    from api.rate_search_routes import get_route_health
    await init_db()

    search_id = uuid4()
    async with get_async_session_maker()() as session:
        rs = RateSearch(
            id=search_id,
            origin="Singapore",
            destination="Melbourne",
            container_type="DRY 20",
            container_quantity=2,
            commodity="Furniture",
            departure_date="2026-08-20",
            selected_carriers=["MAERSK", "CMA"],
            status="COMPLETED"
        )
        csr_maersk = CarrierSearchResult(
            search_id=search_id,
            carrier="MAERSK",
            status="SUCCESS",
            raw_origin_input="Singapore",
            raw_destination_input="Melbourne",
            resolved_origin_name="Singapore",
            resolved_origin_locode="SGSIN",
            resolved_destination_name="Melbourne",
            resolved_destination_locode="AUMEL",
            submitted_origin="Singapore",
            submitted_destination="Melbourne",
            matched_origin="Singapore, Singapore (SGSIN)",
            matched_destination="Melbourne, Australia (AUMEL)",
            has_port_mismatch=False
        )
        session.add(rs)
        session.add(csr_maersk)
        await session.commit()

    async with get_async_session_maker()() as session:
        health_data = await get_route_health(session)
        assert "carriers" in health_data
        assert "routes" in health_data
        assert len(health_data["routes"]) > 0
        
        # Verify Maersk record under Singapore -> Melbourne route
        sing_mel = next((r for r in health_data["routes"] if "Singapore" in r["origin_name"] and "Melbourne" in r["destination_name"]), None)
        assert sing_mel is not None
        assert sing_mel["carrier_health"]["MAERSK"]["status"] == "SUCCESS"
        assert sing_mel["carrier_health"]["MAERSK"]["has_port_mismatch"] is False


if __name__ == "__main__":
    pytest.main([__file__])

