"""Run some carriers on a worker machine (e.g. the office laptop) instead of this server.

Maersk challenges the cloud server's headless-looking browser with an hCaptcha on every
booking search but not a real PC's Chrome. So the laptop runs as a worker for MAERSK:

- The worker is a normal backend started with WORKER_CARRIERS=MAERSK (and the shared
  DATABASE_URL). It writes a heartbeat every few seconds and claims searches handed to it.
- The API server, when a carrier's worker is online, marks that carrier's result row
  worker="remote" with the request attached, and waits while the worker runs it and
  writes the quotes into the shared database. If no worker claims it within
  CLAIM_TIMEOUT_SEC, the server takes it back and runs it itself, as before.
"""
import asyncio
import os
import socket
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update

from models import database
from models.rate_search import CarrierSearchResult, WorkerHeartbeat

REMOTE = "remote"
HEARTBEAT_EVERY_SEC = 10
ONLINE_WITHIN_SEC = 45
CLAIM_TIMEOUT_SEC = float(os.getenv("WORKER_CLAIM_TIMEOUT_SEC", "60"))
POLL_SEC = 2.0

FINISHED = {
    "AVAILABLE_QUOTES_FOUND", "NO_QUOTES_AVAILABLE", "LOGIN_FAILED", "TIMEOUT", "UNKNOWN_ERROR",
    "EXTRACTION_FAILED", "FAILED", "COMPLETED", "SERVICE_UNAVAILABLE", "CONNECTOR_NOT_AVAILABLE",
    "CAPTCHA_OR_MANUAL_REVIEW_REQUIRED",
}


def _maker():
    return database.get_async_session_maker()


def worker_carriers() -> set[str]:
    """Carriers this machine runs as a worker (WORKER_CARRIERS=MAERSK), empty on the API server."""
    return {c.strip().upper() for c in os.getenv("WORKER_CARRIERS", "").split(",") if c.strip()}


def is_worker() -> bool:
    return bool(worker_carriers())


def worker_id() -> str:
    return (os.getenv("WORKER_ID") or socket.gethostname() or "worker")[:100]


async def online_workers() -> list[dict]:
    """Every worker with its carriers, last heartbeat and whether it's online now."""
    cutoff = datetime.utcnow() - timedelta(seconds=ONLINE_WITHIN_SEC)
    async with _maker()() as s:
        rows = (await s.execute(select(WorkerHeartbeat))).scalars().all()
    return [
        {
            "worker_id": r.worker_id,
            "carriers": [c for c in (r.carriers or "").split(",") if c],
            "last_seen": r.last_seen.isoformat() + "Z" if r.last_seen else None,
            "online": bool(r.last_seen and r.last_seen >= cutoff),
        }
        for r in rows
    ]


async def _worker_online_for(carrier_code: str, wid: Optional[str] = None) -> bool:
    for w in await online_workers():
        if w["online"] and carrier_code.upper() in w["carriers"] and (wid is None or w["worker_id"] == wid):
            return True
    return False


async def should_delegate(carrier_code: str) -> bool:
    """True when another machine is online as a worker for this carrier."""
    if carrier_code.upper() in worker_carriers():
        return False  # we are that worker
    try:
        return await _worker_online_for(carrier_code)
    except Exception as e:  # e.g. table not created yet: just run it here
        print(f"[WORKER] Could not check for workers: {e}")
        return False


async def _set(search_id: UUID, carrier_code: str, **values) -> None:
    async with _maker()() as s:
        await s.execute(
            update(CarrierSearchResult)
            .where(CarrierSearchResult.search_id == search_id, CarrierSearchResult.carrier == carrier_code)
            .values(**values)
        )
        await s.commit()


async def delegate_and_wait(search_id: UUID, carrier_code: str, request, total_timeout_sec: float) -> bool:
    """Hand this carrier's search to a worker and wait for it to finish.

    Returns True when the worker (or this function, on a timeout) wrote the final
    status, False when no worker claimed it in time and the caller should run it itself.
    """
    await _set(search_id, carrier_code, worker=REMOTE, worker_request=request.model_dump_json(),
               status="QUEUED", error_message=None)
    print(f"[WORKER] {carrier_code}: handed to the worker machine, waiting for it to pick it up...")
    loop = asyncio.get_running_loop()
    started = loop.time()
    where = (CarrierSearchResult.search_id == search_id, CarrierSearchResult.carrier == carrier_code)
    try:
        while True:
            await asyncio.sleep(POLL_SEC)
            async with _maker()() as s:
                row = (await s.execute(select(CarrierSearchResult.status, CarrierSearchResult.worker).where(*where))).first()
            if not row:
                return True
            status, wid = row
            if status in FINISHED:
                print(f"[WORKER] {carrier_code}: the worker finished ({status}).")
                return True
            waited = loop.time() - started
            if wid == REMOTE and waited > CLAIM_TIMEOUT_SEC:
                async with _maker()() as s:
                    res = await s.execute(
                        update(CarrierSearchResult).where(*where, CarrierSearchResult.worker == REMOTE).values(worker=None)
                    )
                    await s.commit()
                if res.rowcount:
                    print(f"[WORKER] {carrier_code}: no worker picked it up in {CLAIM_TIMEOUT_SEC:.0f}s; running it on this server.")
                    return False
                continue  # claimed just now
            if wid not in (None, REMOTE) and not await _worker_online_for(carrier_code, wid):
                await _set(search_id, carrier_code, status="FAILED", completed_at=datetime.utcnow(),
                           error_message=f"The worker machine ({wid}) went offline during the search.")
                return True
            if waited > total_timeout_sec:
                await _set(search_id, carrier_code, status="TIMEOUT", completed_at=datetime.utcnow(),
                           error_message=f"The worker machine didn't finish within {total_timeout_sec / 60:.0f} min.")
                return True
    except asyncio.CancelledError:
        await asyncio.shield(_set(search_id, carrier_code, status="FAILED", completed_at=datetime.utcnow(),
                                  error_message="Search forcefully stopped by user"))
        raise


async def _heartbeat_loop(carriers: set[str], wid: str) -> None:
    while True:
        try:
            async with _maker()() as s:
                hb = await s.get(WorkerHeartbeat, wid)
                if hb is None:
                    s.add(WorkerHeartbeat(worker_id=wid, carriers=",".join(sorted(carriers)), last_seen=datetime.utcnow()))
                else:
                    hb.carriers = ",".join(sorted(carriers))
                    hb.last_seen = datetime.utcnow()
                await s.commit()
        except Exception as e:
            print(f"[WORKER] Heartbeat failed: {e}")
        await asyncio.sleep(HEARTBEAT_EVERY_SEC)


async def claim_next(carriers: set[str], wid: str) -> Optional[tuple[UUID, str, str]]:
    """Claim one waiting search for these carriers: (search_id, carrier, request JSON) or None."""
    async with _maker()() as s:
        rows = (await s.execute(
            select(CarrierSearchResult.id, CarrierSearchResult.search_id, CarrierSearchResult.carrier, CarrierSearchResult.worker_request)
            .where(
                CarrierSearchResult.worker == REMOTE,
                CarrierSearchResult.status == "QUEUED",  # not one the server already gave up on
                CarrierSearchResult.carrier.in_(list(carriers)),
            )
            .limit(5)
        )).all()
        for row_id, search_id, carrier, req_json in rows:
            res = await s.execute(
                update(CarrierSearchResult)
                .where(CarrierSearchResult.id == row_id, CarrierSearchResult.worker == REMOTE,
                       CarrierSearchResult.status == "QUEUED")
                .values(worker=wid)
            )
            await s.commit()
            if res.rowcount:
                return search_id, carrier, req_json
    return None


async def run_one(carriers: set[str], wid: str) -> bool:
    """Claim and run one waiting search. Returns True if it ran one."""
    from models.schemas import RateSearchRequest
    from services import job_service

    claimed = await claim_next(carriers, wid)
    if not claimed:
        return False
    search_id, carrier, req_json = claimed
    print(f"[WORKER] Claimed {carrier} for search {search_id}.")
    try:
        request = RateSearchRequest.model_validate_json(req_json)
        await job_service.run_carrier_search(search_id, carrier, request, local_only=True)
    except Exception as e:
        print(f"[WORKER] {carrier} for search {search_id} failed: {e}")
        await _set(search_id, carrier, status="UNKNOWN_ERROR", completed_at=datetime.utcnow(),
                   error_message=f"Worker error: {e}")
    finally:
        await job_service.update_search_status(search_id)
    return True


async def _claim_loop(carriers: set[str], wid: str) -> None:
    while True:
        try:
            if not await run_one(carriers, wid):
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[WORKER] Claim loop error: {e}")
            await asyncio.sleep(5)


def start_worker() -> list[asyncio.Task]:
    """Start the heartbeat and claim loops when WORKER_CARRIERS is set (call from app startup)."""
    carriers = worker_carriers()
    if not carriers:
        return []
    wid = worker_id()
    print(f"[WORKER] This machine is a worker '{wid}' for {', '.join(sorted(carriers))}.")
    return [asyncio.create_task(_heartbeat_loop(carriers, wid)), asyncio.create_task(_claim_loop(carriers, wid))]
