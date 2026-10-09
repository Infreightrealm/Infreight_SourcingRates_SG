"""Handing a carrier (Maersk) to a worker machine through the shared database."""
import asyncio
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from models.database import Base
from models.rate_search import CarrierSearchResult, RateSearch, WorkerHeartbeat
from models.schemas import CarrierResultStatus, RateSearchRequest
from services import job_service, remote_worker


class FakeConnector:
    def __init__(self, calls, carrier):
        self.calls, self.carrier = calls, carrier

    async def run_full_search(self, request):
        self.calls.append(self.carrier)
        return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

    async def close(self, *a, **k):
        pass


@pytest.fixture
def db(monkeypatch, tmp_path):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))  # carrier switches: all on
    monkeypatch.delenv("WORKER_CARRIERS", raising=False)
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(job_service, "get_async_session_maker", lambda: maker)
    monkeypatch.setattr(remote_worker, "_maker", lambda: maker)
    monkeypatch.setattr(remote_worker, "POLL_SEC", 0.05)
    calls = []
    monkeypatch.setattr(job_service, "get_connector", lambda c, **k: FakeConnector(calls, c))

    async def setup(heartbeat_age_sec=None):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        sid = uuid.uuid4()
        async with maker() as s:
            s.add(RateSearch(id=sid, origin="Singapore", destination="Hamburg", container_type="DRY 40H", commodity="FAK",
                             departure_date="tomorrow", selected_carriers=["MAERSK"], status="RUNNING"))
            s.add(CarrierSearchResult(search_id=sid, carrier="MAERSK", status="QUEUED"))
            if heartbeat_age_sec is not None:
                s.add(WorkerHeartbeat(worker_id="laptop", carriers="MAERSK",
                                      last_seen=datetime.utcnow() - timedelta(seconds=heartbeat_age_sec)))
            await s.commit()
        return sid

    async def row():
        async with maker() as s:
            return (await s.execute(CarrierSearchResult.__table__.select())).first()

    yield setup, row, calls
    asyncio.run(engine.dispose())


REQ = RateSearchRequest(carriers=["MAERSK"], origin="Singapore", destination="Hamburg", container_types=["DRY 40H"])


def test_should_delegate_only_to_an_online_worker(db, monkeypatch):
    setup, _, _ = db

    async def check(age):
        await setup(age)
        return await remote_worker.should_delegate("MAERSK"), await remote_worker.should_delegate("ONE")

    assert asyncio.run(check(None)) == (False, False)


def test_should_delegate_online_stale_and_self(db, monkeypatch):
    setup, _, _ = db

    async def run():
        await setup(5)
        online = await remote_worker.should_delegate("MAERSK")
        other = await remote_worker.should_delegate("ONE")
        monkeypatch.setenv("WORKER_CARRIERS", "MAERSK")
        self_check = await remote_worker.should_delegate("MAERSK")
        return online, other, self_check

    assert asyncio.run(run()) == (True, False, False)


def test_stale_heartbeat_is_offline(db):
    setup, _, _ = db

    async def run():
        await setup(remote_worker.ONLINE_WITHIN_SEC + 30)
        return await remote_worker.should_delegate("MAERSK")

    assert asyncio.run(run()) is False


def test_worker_runs_the_handed_over_search(db, monkeypatch):
    setup, row, calls = db
    # Server and worker are separate machines with their own per-carrier locks.
    monkeypatch.setattr(job_service.queue_manager, "get_carrier_lock", lambda c: asyncio.Lock())

    async def run():
        sid = await setup(5)
        api = asyncio.create_task(job_service.run_carrier_search(sid, "MAERSK", REQ))
        for _ in range(100):  # wait until the API server has handed it over
            await asyncio.sleep(0.02)
            if (await row()).worker == remote_worker.REMOTE:
                break
        ran = await remote_worker.run_one({"MAERSK"}, "laptop")
        await asyncio.wait_for(api, 5)
        return ran, sid

    ran, sid = asyncio.run(run())
    r = asyncio.run(row())
    assert ran is True
    assert calls == ["MAERSK"]  # ran once, on the worker
    assert r.worker == "laptop" and r.status == "NO_QUOTES_AVAILABLE"


def test_server_runs_it_when_the_worker_goes_offline_unclaimed(db, monkeypatch):
    setup, row, calls = db
    monkeypatch.setattr(remote_worker, "CLAIM_TIMEOUT_SEC", 0.2)

    async def run():
        sid = await setup(remote_worker.ONLINE_WITHIN_SEC - 1)  # online now, stale a second later
        await asyncio.wait_for(job_service.run_carrier_search(sid, "MAERSK", REQ), 10)

    asyncio.run(run())
    r = asyncio.run(row())
    assert calls == ["MAERSK"]
    assert r.worker is None and r.status == "NO_QUOTES_AVAILABLE"


def test_busy_online_worker_is_waited_for_then_server_takes_over(db, monkeypatch):
    setup, row, calls = db
    monkeypatch.setattr(remote_worker, "CLAIM_TIMEOUT_SEC", 0.1)
    monkeypatch.setattr(remote_worker, "BUSY_CLAIM_LIMIT_SEC", 1.0)

    async def run():
        sid = await setup(5)  # online for the whole test, but never claims
        loop = asyncio.get_running_loop()
        t0 = loop.time()
        await asyncio.wait_for(job_service.run_carrier_search(sid, "MAERSK", REQ), 10)
        return loop.time() - t0

    waited = asyncio.run(run())
    assert waited >= 1.0  # not taken back at the 0.1 s claim timeout while the worker is online
    assert calls == ["MAERSK"]
    assert asyncio.run(row()).worker is None


def test_heartbeat_thread_beats_while_the_event_loop_is_blocked(tmp_path, monkeypatch):
    import threading
    import time
    from sqlalchemy.ext.asyncio import create_async_engine as cae
    db_file = tmp_path / "hb.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    monkeypatch.setattr(remote_worker, "HEARTBEAT_EVERY_SEC", 1)

    async def make_tables():
        e = cae(f"sqlite+aiosqlite:///{db_file}")
        async with e.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await e.dispose()

    asyncio.run(make_tables())
    stop = threading.Event()
    t = threading.Thread(target=remote_worker._heartbeat_thread, args=({"MAERSK"}, "laptop", stop), daemon=True)
    t.start()
    time.sleep(2.5)  # the main thread is blocked, like a profile copy blocking the app's loop
    stop.set()
    t.join(5)

    async def read():
        e = cae(f"sqlite+aiosqlite:///{db_file}")
        maker = async_sessionmaker(e, class_=AsyncSession, expire_on_commit=False)
        async with maker() as s:
            hb = await s.get(WorkerHeartbeat, "laptop")
        await e.dispose()
        return hb

    hb = asyncio.run(read())
    assert hb is not None and hb.carriers == "MAERSK"
    assert (datetime.utcnow() - hb.last_seen).total_seconds() < 3


def test_worker_ignores_rows_the_server_gave_up_on(db):
    setup, row, _ = db

    async def run():
        sid = await setup(5)
        async with job_service.get_async_session_maker()() as s:
            r = (await s.execute(CarrierSearchResult.__table__.select())).first()
            await s.execute(CarrierSearchResult.__table__.update().values(worker="remote", status="FAILED"))
            await s.commit()
        return await remote_worker.claim_next({"MAERSK"}, "laptop")

    assert asyncio.run(run()) is None
