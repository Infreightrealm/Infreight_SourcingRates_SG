"""Admin carrier on/off switch: stored on the volume, and a switched-off carrier is
skipped by searches without opening a browser."""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.database import Base
from models.rate_search import CarrierSearchResult, RateSearch
from models.schemas import RateSearchRequest
from services import carrier_switches, job_service


def test_switch_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    assert all(s["enabled"] for s in carrier_switches.get_switches().values())
    carrier_switches.set_switch("one", False, "Site under maintenance", "brian")
    assert carrier_switches.off_message("ONE") == "Switched off by admin: Site under maintenance"
    assert carrier_switches.get_switches()["ONE"]["updated_by"] == "brian"
    carrier_switches.set_switch("ONE", True, "ignored when on", "brian")
    assert carrier_switches.off_message("ONE") is None
    assert carrier_switches.get_switches()["ONE"]["reason"] is None


def test_hapag_api_follows_the_hapag_switch(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    carrier_switches.set_switch("HAPAG_LLOYD", False, None, "brian")
    assert carrier_switches.off_message("HAPAG_LLOYD_API").startswith("Switched off by admin")


def test_switched_off_carrier_is_skipped(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    carrier_switches.set_switch("MAERSK", False, "Portal down", "brian")

    def no_connector(*_a, **_k):
        raise AssertionError("a switched-off carrier must not get a connector")

    monkeypatch.setattr(job_service, "get_connector", no_connector)

    async def run():
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        monkeypatch.setattr(job_service, "get_async_session_maker", lambda: maker)
        sid = uuid.uuid4()
        async with maker() as s:
            s.add(RateSearch(id=sid, origin="Singapore", destination="Jebel Ali", container_type="DRY 20", commodity="FAK", departure_date="tomorrow", selected_carriers=["MAERSK"], status="RUNNING"))
            s.add(CarrierSearchResult(search_id=sid, carrier="MAERSK", status="QUEUED"))
            await s.commit()
        req = RateSearchRequest(carriers=["MAERSK"], origin="Singapore", destination="Jebel Ali", container_types=["DRY 20"])
        await job_service.run_carrier_search(sid, "MAERSK", req)
        await job_service.update_search_status(sid)
        async with maker() as s:
            row = (await s.execute(CarrierSearchResult.__table__.select())).first()
            search = await s.get(RateSearch, sid)
        await engine.dispose()
        return row, search.status

    row, status = asyncio.run(run())
    assert row.status == "SERVICE_UNAVAILABLE"
    assert row.error_message == "Switched off by admin: Portal down"
    assert status == "COMPLETED"
