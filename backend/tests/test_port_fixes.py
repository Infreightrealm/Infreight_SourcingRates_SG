"""Port name fixes: connectors note ports their own search couldn't find, results
store the note, and the admin endpoint groups recent misses next to saved fixes."""
import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.user_routes import fetch_port_fixes
from carriers.base_connector import NotAvailableConnector
from models.database import Base
from models.rate_search import CarrierSearchResult
from services import port_manager
from services.job_service import _store_port_not_found


def test_connector_note_is_copied_onto_the_result():
    connector = NotAvailableConnector("MAERSK")
    assert connector.port_not_found is None
    connector.note_port_not_found("destination", "Al 'Aqabah")
    row = CarrierSearchResult(search_id=uuid.uuid4(), carrier="MAERSK")
    _store_port_not_found(row, connector)
    assert (row.unfound_port_side, row.unfound_port_query) == ("destination", "Al 'Aqabah")


def test_no_note_leaves_the_result_alone():
    row = CarrierSearchResult(search_id=uuid.uuid4(), carrier="ONE")
    _store_port_not_found(row, NotAvailableConnector("ONE"))
    _store_port_not_found(row, None)
    assert row.unfound_port_side is None and row.unfound_port_query is None


def test_saved_fixes_live_on_the_persistent_volume(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    assert port_manager._user_overrides_path() == str(tmp_path / "user_carrier_overrides.json")
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path / "missing"))
    assert port_manager._user_overrides_path() == port_manager._REPO_USER_OVERRIDES_PATH


def _miss(carrier, side, locode, name, typed, hours_ago):
    done = datetime.utcnow() - timedelta(hours=hours_ago)
    row = CarrierSearchResult(
        search_id=uuid.uuid4(),
        carrier=carrier,
        status="NO_QUOTES_AVAILABLE",
        completed_at=done,
        unfound_port_side=side,
        unfound_port_query=typed,
    )
    if side == "origin":
        row.resolved_origin_locode, row.resolved_origin_name = locode, name
    else:
        row.resolved_destination_locode, row.resolved_destination_name = locode, name
    return row


def test_endpoint_groups_recent_misses_and_lists_fixes():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(engine) as session:
            session.add_all([
                _miss("MAERSK", "destination", "JOAQJ", "Al 'Aqabah", "Al 'Aqabah", hours_ago=30),
                _miss("MAERSK", "destination", "JOAQJ", "Al 'Aqabah", "Aqaba", hours_ago=2),
                _miss("CMA_CGM", "origin", "VNHPH", "Haiphong", "Haiphong", hours_ago=24 * 20),  # outside 14 days
            ])
            await session.commit()
            result = await fetch_port_fixes(days=14, actor=None, session=session)
        await engine.dispose()
        return result

    result = asyncio.run(run())
    assert len(result["misses"]) == 1
    miss = result["misses"][0]
    assert (miss["carrier"], miss["key"], miss["searches"]) == ("maersk", "joaqj", 2)
    assert miss["typed"] == "Aqaba"  # the most recent attempt
    assert miss["fix"] == "Aqaba, Jordan"  # built-in Maersk fix for JOAQJ

    joaqj = [f for f in result["fixes"] if f["carrier"] == "maersk" and f["key"] == "joaqj"]
    assert joaqj and joaqj[0]["source"] == "built_in" and joaqj[0]["text"] == "Aqaba, Jordan"
