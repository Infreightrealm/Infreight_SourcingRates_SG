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
        origin=request.origin,
        destination=request.destination,
        service_term=request.service_term,
        container_type=request.container_type,
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

    return RateSearchResultResponse(
        search_id=str(search.id),
        status=search.status,
        origin=search.origin,
        destination=search.destination,
        container_type=search.container_type,
        container_quantity=search.container_quantity,
        commodity=search.commodity,
        created_at=search.created_at.isoformat() if search.created_at else None,
        results=results,
    )
