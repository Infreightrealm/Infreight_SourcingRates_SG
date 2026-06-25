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
from services.queue_manager import queue_manager

active_search_tasks: dict[str, list[asyncio.Task]] = {}


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

            # Set real-time status update callback
            async def update_status_cb(new_status: CarrierResultStatus):
                async with get_async_session_maker()() as cb_session:
                    cb_result_query = select(CarrierSearchResult).where(
                        CarrierSearchResult.search_id == search_id,
                        CarrierSearchResult.carrier == carrier_code,
                    )
                    cb_db_result = (await cb_session.execute(cb_result_query)).scalar_one_or_none()
                    if cb_db_result:
                        cb_db_result.status = new_status.value
                        await cb_session.commit()
                        print(f"[JOB] Real-time status update for {carrier_code}: {new_status.value}")

            connector.status_update_callback = update_status_cb

            # Run searches sequentially for each container type in request.container_types
            all_quotes = []
            final_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
            
            c_types = request.container_types or [request.container_type]
            
            for c_index, c_type in enumerate(c_types):
                print(f"[JOB] {carrier_code}: starting cycle {c_index + 1}/{len(c_types)} for container type {c_type}")
                # Update status in database to show which type we are searching
                async with get_async_session_maker()() as cb_session:
                    cb_db_result = (await cb_session.execute(result_query)).scalar_one_or_none()
                    if cb_db_result:
                        cb_db_result.status = f"RUNNING ({c_type})"
                        await cb_session.commit()

                # Create request copy for this container type
                req_copy = request.model_copy(update={"container_type": c_type})
                
                # Run the full search flow
                status, quotes = await connector.run_full_search(req_copy)
                
                # Inject the current cycle container type into each quote schema if not already set
                for q in quotes:
                    if not q.container_type:
                        q.container_type = c_type
                
                # Add the quotes to our list
                all_quotes.extend(quotes)
                
                # Determine final status
                if status == CarrierResultStatus.AVAILABLE_QUOTES_FOUND or (quotes and len(quotes) > 0):
                    final_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                elif status == CarrierResultStatus.CONNECTOR_NOT_AVAILABLE:
                    if final_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                        final_status = CarrierResultStatus.CONNECTOR_NOT_AVAILABLE
                elif status == CarrierResultStatus.SERVICE_UNAVAILABLE:
                    if final_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                        final_status = CarrierResultStatus.SERVICE_UNAVAILABLE
                elif status == CarrierResultStatus.FAILED:
                    if final_status not in (CarrierResultStatus.AVAILABLE_QUOTES_FOUND, CarrierResultStatus.CONNECTOR_NOT_AVAILABLE):
                        final_status = CarrierResultStatus.FAILED
                else:
                    # Keep existing final_status if it's already successful/partially successful
                    pass

            # Update carrier result status
            db_result.status = final_status.value
            db_result.completed_at = datetime.utcnow()

            if final_status == CarrierResultStatus.CONNECTOR_NOT_AVAILABLE:
                db_result.error_message = f"Connector for {carrier_code} is not yet implemented"
            elif final_status == CarrierResultStatus.SERVICE_UNAVAILABLE:
                db_result.error_message = f"Carrier service/website for {carrier_code} is currently unavailable (maintenance or downtime)"

            # Persist quotes
            for q in all_quotes:
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
                    raw_data_json={
                        "source": q.source, 
                        "ref": q.raw_reference,
                        "routing": q.routing,
                        "free_time": q.free_time
                    },
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

        except BaseException as e:
            if isinstance(e, asyncio.CancelledError):
                db_result.status = CarrierResultStatus.FAILED.value
                db_result.error_message = "Search forcefully stopped by user"
            else:
                db_result.status = CarrierResultStatus.UNKNOWN_ERROR.value
                db_result.error_message = str(e)
            db_result.completed_at = datetime.utcnow()
            await asyncio.shield(session.commit())
            if isinstance(e, asyncio.CancelledError):
                raise
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
    search_str_id = str(search_id)
    try:
        # 1. Enqueue and wait for our turn
        name = request.user_name or "Anonymous"
        search_info = f"{name}'s search ({request.origin} to {request.destination})"
        await queue_manager.enqueue_and_wait(search_str_id, search_info)

        # 2. Run searches with concurrency limits
        # Hapag-Lloyd and ONE take the longest, so prioritize them first so they don't hold up the end of the queue
        slow_carriers = ["HAPAG_LLOYD", "ONE"]
        sorted_carriers = sorted(carriers, key=lambda c: 0 if c.upper() in slow_carriers else 1)

        # Limit concurrent browser instances to prevent resource exhaustion and anti-bot triggers
        # Defaults to 2 to avoid RAM/CPU thrashing on standard cloud/vps environments
        import os
        max_concurrency = int(os.getenv("CARRIER_MAX_CONCURRENCY", "2"))
        semaphore = asyncio.Semaphore(max_concurrency)

        async def run_and_update(c):
            async with semaphore:
                try:
                    await run_carrier_search(search_id, c, request)
                finally:
                    await asyncio.shield(update_search_status(search_id))

        active_tasks = [asyncio.create_task(run_and_update(carrier)) for carrier in sorted_carriers]
        active_search_tasks[search_str_id] = active_tasks

        try:
            await asyncio.gather(*active_tasks, return_exceptions=True)
        finally:
            active_search_tasks.pop(search_str_id, None)

    except BaseException as e:
        print(f"[JOB] run_all_carrier_searches was interrupted or cancelled: {e}")
        
        async def do_cleanup():
            async with get_async_session_maker()() as session:
                # Mark all carrier results that are still QUEUED or RUNNING as FAILED
                results = (await session.execute(
                    select(CarrierSearchResult).where(
                        CarrierSearchResult.search_id == search_id,
                        CarrierSearchResult.status.in_(["QUEUED", "RUNNING"])
                    )
                )).scalars().all()
                for r in results:
                    r.status = CarrierResultStatus.FAILED.value
                    r.error_message = "Search forcefully stopped by user"
                    r.completed_at = datetime.utcnow()
                
                # Mark the main search status as FAILED
                search = (await session.execute(
                    select(RateSearch).where(RateSearch.id == search_id)
                )).scalar_one_or_none()
                if search:
                    search.status = SearchStatus.FAILED.value
                    search.updated_at = datetime.utcnow()
                
                await session.commit()
                
        await asyncio.shield(do_cleanup())
        if isinstance(e, asyncio.CancelledError):
            raise

    # 3. Mark search completed in the queue manager to start the auto-release timeout
    await queue_manager.mark_search_completed(search_str_id)

    # 4. Start a background auto-release poller (300 seconds = 5 minutes timeout)
    async def auto_release_poller():
        while True:
            await asyncio.sleep(10)
            released = await queue_manager.auto_release_check(search_str_id, timeout_seconds=300)
            if released:
                print(f"[QUEUE] Auto-released lock for search {search_str_id} due to timeout.")
                break
            # Stop polling if the search is no longer active
            status = await queue_manager.get_queue_status(search_str_id)
            if status["position"] != 0:
                break

    asyncio.create_task(auto_release_poller())


async def cancel_all_active_searches():
    """Cancel all active search tasks."""
    cancelled_count = 0
    for search_id, tasks in list(active_search_tasks.items()):
        for task in tasks:
            if not task.done():
                task.cancel()
                cancelled_count += 1
    print(f"[JOB] Cancelled {cancelled_count} active search task(s).")
