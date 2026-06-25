"""
Rate Search API Routes.

POST /api/rate-search — Create a new rate search
GET  /api/rate-search/{search_id} — Get status and results
"""
import asyncio
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import get_session
from models.rate_search import RateSearch, CarrierSearchResult
from models.quote import Quote, QuoteCharge
from services.queue_manager import queue_manager
from models.schemas import (
    RateSearchRequest,
    RateSearchCreateResponse,
    RateSearchResultResponse,
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

                free_time=q.raw_data_json.get("free_time") if q.raw_data_json else None,
                source=q.raw_data_json.get("source", "carrier_portal") if q.raw_data_json else "carrier_portal",
                raw_reference=q.raw_data_json.get("ref") if q.raw_data_json else None,
            ))

        results.append(CarrierResultSchema(
            carrier=cr.carrier,
            status=cr.status,
            error_message=cr.error_message,
            quotes=quotes,
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
