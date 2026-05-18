"""
Job Service — orchestrates carrier search jobs.

Creates background tasks per carrier, runs connectors, persists results.
"""
import asyncio
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_async_session_maker
from models.rate_search import RateSearch, CarrierSearchResult
from models.quote import Quote, QuoteCharge
from models.schemas import RateSearchRequest, CarrierResultStatus, SearchStatus
from carriers.registry import get_connector


async def run_carrier_search(
    search_id: UUID,
    carrier_code: str,
    request: RateSearchRequest,
):
    """
    Run a single carrier search job.
    Updates the CarrierSearchResult record throughout.
    """
    async with get_async_session_maker()() as session:
        # Find the carrier result record
        result_query = select(CarrierSearchResult).where(
            CarrierSearchResult.search_id == search_id,
            CarrierSearchResult.carrier == carrier_code,
        )
        db_result = (await session.execute(result_query)).scalar_one_or_none()
        if not db_result:
            print(f"[JOB] No CarrierSearchResult found for {carrier_code}")
            return

        # Mark as RUNNING
        db_result.status = CarrierResultStatus.RUNNING.value
        db_result.started_at = datetime.utcnow()
        await session.commit()

        try:
            # Get the connector (mock or live based on env)
            connector = get_connector(carrier_code)

            # Run the full search flow
            status, quotes = await connector.run_full_search(request)

            # Update carrier result status
            db_result.status = status.value
            db_result.completed_at = datetime.utcnow()

            if status == CarrierResultStatus.CONNECTOR_NOT_AVAILABLE:
                db_result.error_message = f"Connector for {carrier_code} is not yet implemented"

            # Persist quotes
            for q in quotes:
                db_quote = Quote(
                    carrier_result_id=db_result.id,
                    carrier=carrier_code,
                    etd=q.etd,
                    eta=q.eta,
                    transit_time_days=q.transit_time_days,
                    service_name=q.service_name,
                    vessel=q.vessel,
                    container_type=q.container_type,
                    container_quantity=q.container_quantity,
                    currency=q.currency,
                    basic_ocean_freight=q.basic_ocean_freight,
                    discount=q.discount,
                    final_freight_value=q.final_freight_value,
                    raw_data_json={"source": q.source, "ref": q.raw_reference},
                )
                session.add(db_quote)
                await session.flush()  # Get the quote ID

                # Persist included surcharges
                for charge in q.included_freight_surcharges:
                    session.add(QuoteCharge(
                        quote_id=db_quote.id,
                        charge_name=charge.name,
                        amount=charge.amount,
                        currency=charge.currency,
                        category="FREIGHT_SURCHARGE_INCLUDED",
                        included_in_final_value=True,
                        reason=charge.reason,
                    ))

                # Persist excluded charges
                for charge in q.excluded_charges:
                    session.add(QuoteCharge(
                        quote_id=db_quote.id,
                        charge_name=charge.name,
                        amount=charge.amount,
                        currency=charge.currency,
                        category=charge.category or "ORIGIN_CHARGE_EXCLUDED",
                        included_in_final_value=False,
                        reason=charge.reason,
                    ))

                # Persist uncertain charges
                for charge in q.uncertain_charges:
                    session.add(QuoteCharge(
                        quote_id=db_quote.id,
                        charge_name=charge.name,
                        amount=charge.amount,
                        currency=charge.currency,
                        category="UNCERTAIN_EXCLUDED",
                        included_in_final_value=False,
                        reason=charge.reason,
                    ))

                # Persist BOF and discount as charges too
                if q.basic_ocean_freight:
                    session.add(QuoteCharge(
                        quote_id=db_quote.id,
                        charge_name="Basic Ocean Freight",
                        amount=q.basic_ocean_freight,
                        currency=q.currency,
                        category="BASIC_OCEAN_FREIGHT",
                        included_in_final_value=True,
                        reason="Basic ocean freight charge",
                    ))

                if q.discount:
                    session.add(QuoteCharge(
                        quote_id=db_quote.id,
                        charge_name="Discount",
                        amount=q.discount,
                        currency=q.currency,
                        category="DISCOUNT",
                        included_in_final_value=True,
                        reason="Discount/rebate",
                    ))

            await session.commit()
            print(f"[JOB] {carrier_code}: {status.value} — {len(quotes)} quote(s)")

        except Exception as e:
            db_result.status = CarrierResultStatus.UNKNOWN_ERROR.value
            db_result.error_message = str(e)
            db_result.completed_at = datetime.utcnow()
            await session.commit()
            print(f"[JOB] {carrier_code} error: {e}")


async def update_search_status(search_id: UUID):
    """Check all carrier results and update the overall search status."""
    async with get_async_session_maker()() as session:
        search = (await session.execute(
            select(RateSearch).where(RateSearch.id == search_id)
        )).scalar_one_or_none()
        if not search:
            return

        results = (await session.execute(
            select(CarrierSearchResult).where(CarrierSearchResult.search_id == search_id)
        )).scalars().all()

        statuses = [r.status for r in results]

        all_done = all(s not in ("QUEUED", "RUNNING") for s in statuses)
        if not all_done:
            search.status = SearchStatus.RUNNING.value
        else:
            has_success = any(s == "AVAILABLE_QUOTES_FOUND" for s in statuses)
            has_failure = any(s in ("LOGIN_FAILED", "TIMEOUT", "UNKNOWN_ERROR",
                                    "EXTRACTION_FAILED", "FAILED") for s in statuses)

            if has_success and has_failure:
                search.status = SearchStatus.PARTIAL_COMPLETED.value
            elif has_success:
                search.status = SearchStatus.COMPLETED.value
            elif has_failure:
                search.status = SearchStatus.FAILED.value
            else:
                search.status = SearchStatus.COMPLETED.value

        search.updated_at = datetime.utcnow()
        await session.commit()


async def run_all_carrier_searches(
    search_id: UUID,
    carriers: list[str],
    request: RateSearchRequest,
):
    """Run search jobs for all selected carriers concurrently, updating overall status as each finishes."""
    async def run_and_update(c):
        try:
            await run_carrier_search(search_id, c, request)
        finally:
            await update_search_status(search_id)

    tasks = [run_and_update(carrier) for carrier in carriers]
    await asyncio.gather(*tasks, return_exceptions=True)
