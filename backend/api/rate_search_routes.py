"""
Rate Search API Routes.

POST /api/rate-search — Create a new rate search
GET  /api/rate-search/{search_id} — Get status and results
"""
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import get_session
from models.rate_search import RateSearch, CarrierSearchResult
from models.quote import Quote, QuoteCharge
from services.queue_manager import queue_manager
from services.port_manager import search_port
from models.schemas import (
    RateSearchRequest,
    RateSearchCreateResponse,
    RateSearchResultResponse,
    BatchRateSearchRequest,
    BatchRateSearchResponse,
    BatchSearchStatusItem,
    CarrierResultSchema,
    QuoteSchema,
    ChargeSchema,
    ALL_CARRIERS,
)
from services.job_service import run_all_carrier_searches

router = APIRouter(prefix="/api", tags=["rate-search"])


@router.post("/rate-search", response_model=RateSearchCreateResponse)
async def create_rate_search(
    request: RateSearchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Create a new rate search and dispatch carrier jobs."""

    # Resolve "ALL" to all carrier codes
    carriers = request.carriers
    if "ALL" in [c.upper() for c in carriers]:
        carriers = ALL_CARRIERS
    else:
        carriers = [c.upper() for c in carriers]

    # Validate carrier codes
    invalid = [c for c in carriers if c not in ALL_CARRIERS]
    if invalid:
        raise HTTPException(400, f"Invalid carrier codes: {invalid}")

    # Create the rate search record
    search = RateSearch(
        user_name=request.user_name,
        origin=request.origin,
        destination=request.destination,
        service_term=request.service_term,
        container_type=", ".join(request.container_types),
        container_quantity=request.container_quantity,
        weight_per_container_kg=request.weight_per_container_kg,
        commodity=request.commodity,
        departure_date=request.departure_date,
        search_window_days=request.search_window_days,
        selected_carriers=carriers,
        status="QUEUED",
    )
    session.add(search)
    await session.flush()

    # Create carrier result records
    for carrier in carriers:
        session.add(CarrierSearchResult(
            search_id=search.id,
            carrier=carrier,
            status="QUEUED",
        ))

    await session.commit()

    # Dispatch background jobs
    background_tasks.add_task(
        run_all_carrier_searches,
        search.id,
        carriers,
        request,
    )

    return RateSearchCreateResponse(
        search_id=str(search.id),
        status="QUEUED",
    )


@router.post("/rate-search/batch", response_model=BatchRateSearchResponse)
async def create_batch_rate_search(
    request: BatchRateSearchRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.
    Dispatches 7 persistent carrier workers concurrently.
    """
    from services.job_service import run_vertical_batch_searches

    carriers = request.carriers
    if "ALL" in [c.upper() for c in carriers]:
        carriers = ALL_CARRIERS
    else:
        carriers = [c.upper() for c in carriers]

    batch_id = str(uuid4())
    search_ids = []
    requests_meta = []

    # Multi-port hygiene BEFORE spending N carriers x M routes of browser time:
    #  - resolve each name to a UN/LOCODE and de-duplicate on the LOCODE pair, so
    #    "SAVANNAH" / "SAVANNAH GEORGIA" or "AL-SOKHNA" / "SOKHNA" don't run twice
    #    (the frontend only dedupes on the exact lowercase string);
    #  - surface names that resolve to nothing as warnings up front instead of
    #    burning every carrier on a route that can only end in "no quotes".
    import difflib
    warnings: list[str] = []
    deduped: list = []
    kept: list[tuple[tuple[str, str], tuple[str, str]]] = []  # ((o_code, d_code), (o_norm, d_norm))

    import re as _re

    def _norm(name: str) -> str:
        # Drop parentheticals ("Nhava Sheva (Jawaharlal Nehru)") so a legit resolution
        # isn't penalised for the port's long official name.
        base = _re.sub(r"\s*\([^)]*\)", "", (name or "").lower())
        return " ".join(base.replace("-", " ").replace("/", " ").split())

    def _contains(a: str, b: str) -> bool:
        na, nb = _norm(a), _norm(b)
        return bool(na) and bool(nb) and (na in nb or nb in na)

    def _resolve(name: str) -> tuple[str, str]:
        """(LOCODE-or-normalized-name, resolved port name). search_port() will
        confidently return SOMETHING for almost any string (e.g. a typo of Saskatoon
        resolves to a Liberian port), so the code alone is never trusted as identity."""
        clean = (name or "").strip()
        try:
            hits = search_port(clean)
        except Exception:
            hits = []
        if hits:
            return (hits[0].get("code") or clean).upper(), str(hits[0].get("name") or "")
        return _norm(clean), ""

    def _looks_like(a: str, b: str) -> bool:
        # Same name with a qualifier ("SAVANNAH" / "SAVANNAH GEORGIA") or a near typo
        # ("DILIKELESI" / "DILISKELESI") both count as the same place.
        return _contains(a, b) or difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio() >= 0.8

    for route in request.routes:
        o_code, o_port = _resolve(route.origin)
        d_code, d_port = _resolve(route.destination)
        # Pre-flight sanity: flag names that barely resemble the port they resolved to
        # (a typo of Saskatoon resolving to "Sasstown", "AL-SOKHNA" to "Balakhna"), so a
        # bad spelling is caught before it burns every carrier's browser time.
        for label, raw, port, code in (("Origin", route.origin, o_port, o_code),
                                       ("Destination", route.destination, d_port, d_code)):
            if port and not _contains(raw, port) and \
                    difflib.SequenceMatcher(None, _norm(raw), _norm(port)).ratio() < 0.75:
                warnings.append(f"{label} '{raw}' resolved to '{port} ({code})' — please verify the spelling.")

        # Collapse a route ONLY when the LOCODE pair matches AND both names are
        # near-identical to a kept route's names (SAVANNAH vs SAVANNAH GEORGIA,
        # DILIKELESI vs DILISKELESI). Same LOCODE with dissimilar names is left alone —
        # it may be the resolver guessing, and a duplicate run is cheaper than a lost lane.
        is_dup = False
        for (kc, kn) in kept:
            if kc == (o_code, d_code) and _looks_like(route.origin, kn[0]) and _looks_like(route.destination, kn[1]):
                is_dup = True
                break
        if is_dup:
            continue
        kept.append(((o_code, d_code), (route.origin, route.destination)))
        deduped.append(route)
    deduplicated_routes = len(request.routes) - len(deduped)
    if deduplicated_routes:
        print(f"[VERTICAL BATCH] Collapsed {deduplicated_routes} duplicate route(s) by LOCODE pair.")

    # Enforce anti-bot safety limit of 200 routes per inquiry (supports 168 port pair RFQs)
    routes = deduped[:200]
    if len(deduped) > 200:
        print(f"[VERTICAL BATCH] Enforced anti-bot safety cap: sliced {len(deduped)} routes to first 200 max.")
        warnings.append(f"Only the first 200 of {len(deduped)} unique routes were queued (anti-bot cap).")

    for route in routes:
        req_obj = RateSearchRequest(
            carriers=carriers,
            origin=route.origin,
            destination=route.destination,
            service_term="CY/CY",
            container_types=route.container_types or ["DRY 20", "DRY 40"],
            weight_per_container_kg=route.weight_per_container_kg or 25000.0,
            commodity=request.commodity or "Furniture",
            user_name=request.user_name,
            search_mode=request.search_mode or "quick"
        )
        requests_meta.append(req_obj)

        search = RateSearch(
            user_name=request.user_name,
            origin=route.origin,
            destination=route.destination,
            service_term="CY/CY",
            container_type=", ".join(req_obj.container_types),
            container_quantity=1,
            weight_per_container_kg=req_obj.weight_per_container_kg,
            commodity=req_obj.commodity,
            departure_date="tomorrow",
            search_window_days=14,
            selected_carriers=carriers,
            status="QUEUED",
        )
        session.add(search)
        await session.flush()
        search_ids.append(search.id)

        for carrier in carriers:
            session.add(CarrierSearchResult(
                search_id=search.id,
                carrier=carrier,
                status="QUEUED",
            ))

    await session.commit()

    background_tasks.add_task(
        run_vertical_batch_searches,
        search_ids,
        carriers,
        requests_meta
    )

    return BatchRateSearchResponse(
        batch_id=batch_id,
        total_routes=len(routes),
        carriers=carriers,
        search_ids=[str(s) for s in search_ids],
        status="QUEUED",
        deduplicated_routes=deduplicated_routes,
        warnings=warnings,
    )


@router.get("/rate-search/status", response_model=List[BatchSearchStatusItem])
async def get_batch_search_status(
    ids: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Lightweight bulk status for batch polling: one request for up to 200 searches,
    returning per-search + per-carrier status and a quote COUNT — no quote or charge
    payloads. Replaces the per-search pollers (168 routes x one 2s poller each was
    ~84 req/s against the full 3-level eager-load results endpoint).
    Declared before /rate-search/{search_id} so it takes routing precedence.
    """
    id_list: list[UUID] = []
    for raw in ids.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            id_list.append(UUID(raw))
        except ValueError:
            continue
    id_list = id_list[:200]
    if not id_list:
        return []

    searches = (await session.execute(
        select(RateSearch.id, RateSearch.status, RateSearch.origin, RateSearch.destination)
        .where(RateSearch.id.in_(id_list))
    )).all()

    carrier_rows = (await session.execute(
        select(
            CarrierSearchResult.search_id,
            CarrierSearchResult.carrier,
            CarrierSearchResult.status,
            func.count(Quote.id),
        )
        .outerjoin(Quote, Quote.carrier_result_id == CarrierSearchResult.id)
        .where(CarrierSearchResult.search_id.in_(id_list))
        .group_by(CarrierSearchResult.search_id, CarrierSearchResult.carrier, CarrierSearchResult.status)
    )).all()

    per_search: dict[UUID, dict] = {}
    for s_id, carrier, status, q_count in carrier_rows:
        entry = per_search.setdefault(s_id, {"carriers": {}, "quote_count": 0})
        entry["carriers"][carrier] = status
        entry["quote_count"] += int(q_count or 0)

    running = {"QUEUED", "RUNNING", "WAITING_FOR_HUMAN_VERIFICATION", "MANUAL_ACTION_REQUIRED"}
    out: list[BatchSearchStatusItem] = []
    for s_id, s_status, origin, destination in searches:
        entry = per_search.get(s_id, {"carriers": {}, "quote_count": 0})
        carrier_statuses = entry["carriers"]
        has_active = any((st in running) or str(st).startswith("RUNNING") for st in carrier_statuses.values())
        is_terminal = (s_status in ("COMPLETED", "PARTIAL_COMPLETED", "FAILED")) and not has_active
        out.append(BatchSearchStatusItem(
            search_id=str(s_id),
            status=s_status,
            origin=origin,
            destination=destination,
            carriers=carrier_statuses,
            quote_count=entry["quote_count"],
            is_terminal=is_terminal,
        ))
    return out


@router.get("/rate-search/{search_id}", response_model=RateSearchResultResponse)
async def get_rate_search(
    search_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get the status and results of a rate search."""

    # Load search with carrier results
    query = (
        select(RateSearch)
        .where(RateSearch.id == search_id)
        .options(
            selectinload(RateSearch.carrier_results)
            .selectinload(CarrierSearchResult.quotes)
            .selectinload(Quote.charges)
        )
    )
    search = (await session.execute(query)).scalar_one_or_none()

    if not search:
        raise HTTPException(404, "Search not found")

    # Build response
    results = []
    for cr in search.carrier_results:
        quotes = []
        for q in cr.quotes:
            # Organize charges by category
            included = []
            excluded = []
            uncertain = []
            for ch in q.charges:
                cs = ChargeSchema(
                    name=ch.charge_name,
                    amount=ch.amount,
                    currency=ch.currency or "USD",
                    category=ch.category,
                    reason=ch.reason,
                )
                if ch.category == "FREIGHT_SURCHARGE_INCLUDED":
                    included.append(cs)
                elif ch.category in ("ORIGIN_CHARGE_EXCLUDED", "DESTINATION_CHARGE_EXCLUDED"):
                    excluded.append(cs)
                elif ch.category == "UNCERTAIN_EXCLUDED":
                    uncertain.append(cs)

            quotes.append(QuoteSchema(
                etd=q.etd,
                eta=q.eta,
                transit_time_days=q.transit_time_days,
                service_name=q.service_name,
                vessel=q.vessel,
                container_type=q.container_type,
                container_quantity=q.container_quantity,
                currency=q.currency or "USD",
                basic_ocean_freight=q.basic_ocean_freight or 0,
                discount=q.discount or 0,
                included_freight_surcharges=included,
                excluded_charges=excluded,
                uncertain_charges=uncertain,
                final_freight_value=q.final_freight_value or 0,
                validity_till=q.validity_till,
                routing=q.raw_data_json.get("routing") if q.raw_data_json else "Direct",

                free_time=getattr(q, "free_time", None) if getattr(q, "free_time", None) is not None else (q.raw_data_json.get("free_time") if q.raw_data_json else None),
                demurrage=getattr(q, "demurrage", None) if getattr(q, "demurrage", None) is not None else (q.raw_data_json.get("demurrage") if q.raw_data_json else None),
                detention=getattr(q, "detention", None) if getattr(q, "detention", None) is not None else (q.raw_data_json.get("detention") if q.raw_data_json else None),
                source=q.raw_data_json.get("source", "carrier_portal") if q.raw_data_json else "carrier_portal",
                raw_reference=q.raw_data_json.get("ref") if q.raw_data_json else None,
            ))

        results.append(CarrierResultSchema(
            carrier=cr.carrier,
            status=cr.status,
            error_message=cr.error_message,
            quotes=quotes,
            raw_origin_input=cr.raw_origin_input,
            raw_destination_input=cr.raw_destination_input,
            resolved_origin_name=cr.resolved_origin_name,
            resolved_origin_locode=cr.resolved_origin_locode,
            resolved_destination_name=cr.resolved_destination_name,
            resolved_destination_locode=cr.resolved_destination_locode,
            submitted_origin=cr.submitted_origin,
            submitted_destination=cr.submitted_destination,
            matched_origin=cr.matched_origin,
            matched_destination=cr.matched_destination,
            has_port_mismatch=cr.has_port_mismatch,
            mismatch_warning=cr.mismatch_warning,
        ))


    # Get queue status
    queue_status = await queue_manager.get_queue_status(str(search.id))

    return RateSearchResultResponse(
        search_id=str(search.id),
        status=search.status,
        origin=search.origin,
        destination=search.destination,
        container_type=search.container_type,
        container_types=[c.strip() for c in search.container_type.split(",")] if search.container_type else None,
        container_quantity=search.container_quantity,
        commodity=search.commodity,
        created_at=search.created_at.isoformat() if search.created_at else None,
        queue_position=queue_status["position"],
        active_search_info=queue_status["active_search_info"],
        results=results,
    )

@router.post("/rate-search/{search_id}/release")
async def release_rate_search(search_id: UUID):
    """Release the queue lock for a completed or queued search."""
    released = await queue_manager.release_lock(str(search_id))
    return {"status": "SUCCESS", "released": released}


# ──────────────────────────────────────────────────────────────────────────────
# AI Chat & Selector Self-Healing Endpoints
# ──────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel
from agent.chat_service import handle_chat_query
from agent.selector_memory import save_approved_selector, reject_selector

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ApproveRepairRequest(BaseModel):
    carrier: str
    step_name: str
    original_selector: str
    approved_selector: str

class RejectRepairRequest(BaseModel):
    carrier: str
    step_name: str

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Chatbot helper endpoint powered by Gemini API."""
    reply = await handle_chat_query(req.message, req.history)
    return {"reply": reply}

@router.get("/connector-repair/reports")
async def get_repair_reports():
    """Scans the diagnostics directory for pending repair reports."""
    import os
    import json
    
    diagnostics_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "diagnostics"
    )
    reports = []
    
    if not os.path.exists(diagnostics_dir):
        return reports
        
    # Walk diagnostics directories to find repair_report.json files
    for entry in os.scandir(diagnostics_dir):
        if entry.is_dir():
            report_file = os.path.join(entry.path, "repair_report.json")
            if os.path.exists(report_file):
                try:
                    with open(report_file, "r", encoding="utf-8") as f:
                        report_data = json.load(f)
                        # Check status of the report in selector memory
                        from agent.selector_memory import _load_memory
                        memory = _load_memory()
                        carrier_key = report_data.get("carrier", "").upper()
                        step_name = report_data.get("step_name", "")
                        
                        step_memory = memory.get(carrier_key, {}).get(step_name, {})
                        if step_memory:
                            report_data["status"] = step_memory.get("status", "PENDING_REVIEW")
                        else:
                            report_data["status"] = "PENDING_REVIEW"
                            
                        # Add diagnostic directory name
                        report_data["dir_name"] = entry.name
                        reports.append(report_data)
                except Exception as e:
                    print(f"[API] Error reading report {report_file}: {e}")
                    
    return reports

@router.post("/connector-repair/approve")
async def approve_repair(req: ApproveRepairRequest):
    """Approves a suggested AI selector fix and saves it to memory."""
    save_approved_selector(
        carrier=req.carrier,
        step_name=req.step_name,
        original_selector=req.original_selector,
        approved_selector=req.approved_selector
    )
    return {"status": "SUCCESS", "message": "Selector repair approved and saved."}

@router.post("/connector-repair/reject")
async def reject_repair(req: RejectRepairRequest):
    """Rejects a suggested AI selector fix, marking it as rejected in memory."""
    reject_selector(carrier=req.carrier, step_name=req.step_name)
    return {"status": "SUCCESS", "message": "Selector repair rejected."}


@router.post("/force-stop")
async def force_stop_searches():
    """Forcefully clears the queue and cancels all active search tasks."""
    from services.queue_manager import queue_manager
    from services.job_service import cancel_all_active_searches
    await queue_manager.force_clear_all()
    await cancel_all_active_searches()
    return {"status": "SUCCESS", "message": "Search Queue forcefully cleared and all active searches cancelled."}


@router.get("/admin/route-health")
async def get_route_health(session: AsyncSession = Depends(get_session)):
    """
    Get carrier search reliability & route health matrix across origin-destination pairs.
    """
    stmt = (
        select(CarrierSearchResult, RateSearch)
        .join(RateSearch, CarrierSearchResult.search_id == RateSearch.id)
        .options(selectinload(CarrierSearchResult.quotes))
        .order_by(RateSearch.created_at.desc())
    )

    res = await session.execute(stmt)
    records = res.all()

    CARRIERS = ["MAERSK", "CMA", "ONE", "HAPAG", "MSC", "OOCL", "GREENX"]
    routes_map = {}

    for csr, rs in records:
        origin = rs.origin or csr.resolved_origin_name or "Unknown"
        dest = rs.destination or csr.resolved_destination_name or "Unknown"
        orig_code = csr.resolved_origin_locode or ""
        dest_code = csr.resolved_destination_locode or ""

        route_key = f"{origin} -> {dest}"

        if route_key not in routes_map:
            routes_map[route_key] = {
                "route_key": route_key,
                "origin_name": origin,
                "origin_locode": orig_code,
                "destination_name": dest,
                "destination_locode": dest_code,
                "carrier_health": {c: None for c in CARRIERS}
            }

        carrier_raw = (csr.carrier or "").upper()
        carrier_code_map = {
            "CMA_CGM": "CMA",
            "CMA": "CMA",
            "HAPAG_LLOYD": "HAPAG",
            "HAPAG": "HAPAG",
            "MAERSK": "MAERSK",
            "ONE": "ONE",
            "MSC": "MSC",
            "OOCL": "OOCL",
            "GREENX": "GREENX"
        }
        carrier = carrier_code_map.get(carrier_raw, carrier_raw)

        if carrier in CARRIERS and routes_map[route_key]["carrier_health"][carrier] is None:
            quotes_count = len(csr.quotes) if csr.quotes else 0
            
            raw_status = (csr.status or "").upper()
            if quotes_count > 0 or raw_status in ["COMPLETED", "SUCCESS", "FINISHED"]:
                status = "SUCCESS" if (quotes_count > 0 or raw_status in ["COMPLETED", "SUCCESS"]) else "NO_QUOTES_AVAILABLE"
                if quotes_count == 0 and raw_status in ["COMPLETED", "SUCCESS"]:
                    status = "NO_QUOTES_AVAILABLE"
            elif raw_status in ["NO_QUOTES_AVAILABLE", "NO_QUOTES"]:
                status = "NO_QUOTES_AVAILABLE"
            else:
                status = "FAILED"

            routes_map[route_key]["carrier_health"][carrier] = {
                "status": status,
                "quotes_count": quotes_count,
                "last_searched_at": csr.completed_at.isoformat() if csr.completed_at else (csr.started_at.isoformat() if csr.started_at else None),
                "raw_origin_input": csr.raw_origin_input or rs.origin,
                "raw_destination_input": csr.raw_destination_input or rs.destination,
                "submitted_origin": csr.submitted_origin,
                "submitted_destination": csr.submitted_destination,
                "matched_origin": csr.matched_origin,
                "matched_destination": csr.matched_destination,
                "has_port_mismatch": csr.has_port_mismatch,
                "mismatch_warning": csr.mismatch_warning,
                "error_message": csr.error_message
            }

    return {
        "carriers": CARRIERS,
        "routes": list(routes_map.values())
    }


from sqlalchemy.orm import selectinload

@router.get("/admin/search-history")
@router.get("/searches/history")
async def get_user_search_history(
    user_name: Optional[str] = None,
    limit: int = 250,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed historical rate searches per user including timestamps, routes, cargo specs, and carrier results.
    """
    stmt = (
        select(RateSearch)
        .options(selectinload(RateSearch.carrier_results).selectinload(CarrierSearchResult.quotes))
        .order_by(RateSearch.created_at.desc())
        .limit(min(limit, 500))
    )
    if user_name:
        stmt = stmt.where(RateSearch.user_name.ilike(f"%{user_name.strip()}%"))

    res = await session.execute(stmt)
    searches = res.scalars().all()

    history = []
    for rs in searches:
        carrier_summaries = []
        total_quotes = 0
        for csr in rs.carrier_results:
            q_count = len(csr.quotes) if csr.quotes else 0
            total_quotes += q_count
            carrier_summaries.append({
                "carrier": csr.carrier,
                "status": csr.status,
                "error_message": csr.error_message,
                "quotes_count": q_count
            })

        effective_status = rs.status
        running_states = {"QUEUED", "RUNNING", "WAITING_FOR_HUMAN_VERIFICATION", "MANUAL_ACTION_REQUIRED"}
        if rs.carrier_results:
            any_running = any(
                cr.status in running_states or (cr.status.startswith("RUNNING") if cr.status else False)
                for cr in rs.carrier_results
            )
            if any_running:
                # If any carrier is still queued or running, keep search status as QUEUED or RUNNING
                effective_status = "RUNNING" if rs.status == "RUNNING" or any(cr.status.startswith("RUNNING") for cr in rs.carrier_results) else "QUEUED"
            else:
                has_succ = any(cr.status == "AVAILABLE_QUOTES_FOUND" or (cr.quotes and len(cr.quotes) > 0) for cr in rs.carrier_results)
                effective_status = "COMPLETED" if has_succ else "FAILED"

        history.append({
            "id": str(rs.id),
            "user_name": rs.user_name or "Guest User",
            "created_at": (rs.created_at.isoformat() + ("Z" if not rs.created_at.isoformat().endswith("Z") else "")) if rs.created_at else "",
            "origin": rs.origin,
            "destination": rs.destination,
            "container_type": rs.container_type,
            "container_quantity": rs.container_quantity,
            "weight_per_container_kg": rs.weight_per_container_kg,
            "commodity": rs.commodity,
            "departure_date": rs.departure_date,
            "selected_carriers": rs.selected_carriers or [],
            "status": effective_status,
            "total_quotes": total_quotes,
            "carrier_results": carrier_summaries
        })

    return history

