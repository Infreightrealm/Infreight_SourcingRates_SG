"""
A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC per
container size, marked TIMEOUT with its browser closed, so the search can finish.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import select

import services.job_service as job_service
from models.database import get_async_session_maker, init_db
from models.rate_search import RateSearch, CarrierSearchResult
from models.schemas import RateSearchRequest, CarrierResultStatus


class HangingConnector:
    """Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest."""

    def __init__(self, hang_on: set[str]):
        self.hang_on = hang_on
        self.status_update_callback = None
        self.last_error_message = None
        self.closed_runs: list[str] = []

    async def run_full_search(self, request):
        try:
            if request.container_type in self.hang_on:
                await asyncio.Event().wait()  # never set: a frozen page
            return CarrierResultStatus.NO_QUOTES_AVAILABLE, []
        finally:
            # Mirrors BaseCarrierConnector.run_full_search closing its browser.
            self.closed_runs.append(request.container_type)

    async def close(self):
        pass


async def _run(monkeypatch, connector, container_types):
    await init_db()
    search_id = uuid4()
    async with get_async_session_maker()() as session:
        session.add(RateSearch(
            id=search_id, origin="Singapore", destination="Toronto",
            container_type=container_types[0], container_quantity=1,
            commodity="Furniture", departure_date="2026-10-07",
            selected_carriers=["ONE"], status="RUNNING",
        ))
        session.add(CarrierSearchResult(search_id=search_id, carrier="ONE", status="QUEUED"))
        await session.commit()

    monkeypatch.setattr(job_service, "CARRIER_SEARCH_TIMEOUT_SEC", 0.5)
    monkeypatch.setattr(job_service, "get_connector", lambda *a, **k: connector)
    req = RateSearchRequest(
        origin="Singapore", destination="Toronto",
        container_type=container_types[0], container_types=container_types,
        container_quantity=1, commodity="Furniture", departure_date="2026-10-07",
        carriers=["ONE"],
    )

    started = asyncio.get_running_loop().time()
    await asyncio.wait_for(job_service.run_carrier_search(search_id, "ONE", req), timeout=10)
    elapsed = asyncio.get_running_loop().time() - started

    async with get_async_session_maker()() as session:
        result = (await session.execute(
            select(CarrierSearchResult).where(CarrierSearchResult.search_id == search_id)
        )).scalar_one()
    return result, elapsed


@pytest.mark.asyncio
async def test_hung_carrier_times_out_per_container_size(monkeypatch):
    connector = HangingConnector(hang_on={"DRY 20", "DRY 40H"})
    result, elapsed = await _run(monkeypatch, connector, ["DRY 20", "DRY 40H"])

    assert result.status == CarrierResultStatus.TIMEOUT.value
    assert "DRY 20" in result.error_message and "DRY 40H" in result.error_message
    assert result.completed_at is not None
    assert connector.closed_runs == ["DRY 20", "DRY 40H"]  # each hung run was cancelled and cleaned up
    assert elapsed < 5


@pytest.mark.asyncio
async def test_timeout_on_one_size_still_runs_the_next(monkeypatch):
    connector = HangingConnector(hang_on={"DRY 20"})
    result, _ = await _run(monkeypatch, connector, ["DRY 20", "DRY 40H"])

    assert connector.closed_runs == ["DRY 20", "DRY 40H"]
    assert result.status == CarrierResultStatus.TIMEOUT.value
    assert "DRY 20" in result.error_message and "DRY 40H" not in result.error_message
