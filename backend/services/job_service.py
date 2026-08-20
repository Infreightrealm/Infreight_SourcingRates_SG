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
import re
import difflib
from services.port_manager import search_port, COUNTRY_CODE_TO_NAME
from services.queue_manager import queue_manager


def _detect_port_mismatch(

    resolved_name: str | None,
    resolved_locode: str | None,
    matched_port_str: str | None,
) -> bool | None:
    """
    Detects port mismatch for origin or destination.
    Returns:
    - True if verified mismatch (matched_port_str exists and differs from target port)
    - False if verified match (matched_port_str matches target UN/LOCODE or City Name + Country Code)
    - None if unknown / could not verify (matched_port_str is null or empty)
    """
    if not matched_port_str or not matched_port_str.strip():
        return None  # UNKNOWN / Could Not Verify

    matched_clean = matched_port_str.strip().lower()

    # 0. Direct match: if resolved_name is contained in matched_clean or vice versa
    if resolved_name:
        r_clean = resolved_name.strip().lower()
        if r_clean and (r_clean in matched_clean or matched_clean in r_clean):
            return False

    # 1. Direct 5-letter UN/LOCODE extraction from matched_port_str if present (e.g. MYPGU, SGSIN)
    # Must be uppercase 5-letter code with valid ISO country prefix to avoid matching words like 'Pasir' or 'Johor'
    locode_matches = re.findall(r'\b([A-Z]{5})\b', matched_port_str)
    for extracted_code in locode_matches:
        if extracted_code[:2] in COUNTRY_CODE_TO_NAME:
            if resolved_locode:
                if extracted_code == resolved_locode.upper():
                    return False
                else:
                    return True


    # 2. Extract 2-letter ISO Country Code from LOCODE (e.g. SGSIN -> SG, DEHAM -> DE, MYPKG -> MY)
    country_code = resolved_locode[:2].lower() if (resolved_locode and len(resolved_locode) >= 2) else None
    country_name = COUNTRY_CODE_TO_NAME.get(country_code.upper(), "").lower() if country_code else None

    # 3. City Name & Country Code check
    if resolved_name:
        name_clean = resolved_name.strip().lower()
        
        # Known city name synonyms (e.g. Kochi <-> Cochin, Nhava Sheva <-> Jawaharlal Nehru)
        SYNONYMS = {
            "kochi": ["cochin", "kerala"],
            "cochin": ["kochi", "kerala"],
            "nhava sheva": ["jawaharlal", "nehru"],
            "jawaharlal nehru": ["nhava sheva"],
            "haiphong": ["hai phong"],
            "hai phong": ["haiphong"],
            "ho chi minh": ["sai gon"],
        }
        
        # Split into significant words (excluding generic logistics noise)
        city_keywords = [
            w for w in re.split(r'[\s,()/\-]+', name_clean)
            if len(w) > 2 and w not in ["port", "the", "and", "city", "pat"]
        ]
        
        # Add synonyms to keywords list
        for kw in list(city_keywords):
            if kw in SYNONYMS:
                city_keywords.extend(SYNONYMS[kw])
        
        has_city_match = False
        if city_keywords:
            for kw in city_keywords:
                if kw in matched_clean:
                    has_city_match = True
                    break
                for matched_word in re.split(r'[\s,()/\-]+', matched_clean):
                    if len(matched_word) > 2:
                        ratio = difflib.SequenceMatcher(None, kw, matched_word).ratio()
                        if ratio >= 0.75:
                            has_city_match = True
                            break
        else:
            has_city_match = (name_clean in matched_clean)

        has_country_match = True
        if country_code:
            country_pattern = r'\b' + re.escape(country_code) + r'\b'
            if re.search(country_pattern, matched_clean) or (country_name and country_name in matched_clean):
                has_country_match = True
            else:
                # Exclude 2-letter codes that collide with common English words / abbreviations
                common_prepositions = {"in", "or", "is", "at", "so", "to", "by", "no", "me", "it", "an", "as", "do"}
                other_country_matches = [
                    code.lower() for code, name in COUNTRY_CODE_TO_NAME.items()
                    if code.lower() != country_code and code.lower() not in common_prepositions and (
                        re.search(r'\b' + re.escape(code.lower()) + r'\b', matched_clean) or
                        (len(name) > 3 and name.lower() in matched_clean)
                    )
                ]
                if other_country_matches:
                    has_country_match = False

        if has_city_match and has_country_match:
            return False

    return True





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

        connector = None
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

            # Update carrier result status and completed timestamp
            db_result.status = final_status.value
            db_result.completed_at = datetime.utcnow()

            # Resolve system-level ports for observability
            orig_matches = search_port(request.origin)
            res_orig_name = orig_matches[0]["name"] if orig_matches else request.origin
            res_orig_locode = orig_matches[0]["code"] if orig_matches else None

            dest_matches = search_port(request.destination)
            res_dest_name = dest_matches[0]["name"] if dest_matches else request.destination
            res_dest_locode = dest_matches[0]["code"] if dest_matches else None

            submitted_orig = getattr(connector, "submitted_origin", None) or request.origin
            submitted_dest = getattr(connector, "submitted_destination", None) or request.destination
            matched_orig = getattr(connector, "matched_origin", None)
            matched_dest = getattr(connector, "matched_destination", None)

            orig_mismatch = _detect_port_mismatch(res_orig_name, res_orig_locode, matched_orig)
            dest_mismatch = _detect_port_mismatch(res_dest_name, res_dest_locode, matched_dest)

            if orig_mismatch is True or dest_mismatch is True:
                has_port_mismatch = True
                warnings = []
                if orig_mismatch is True:
                    warnings.append(f"Origin mismatch: carrier matched '{matched_orig}' vs requested '{res_orig_name}' ({res_orig_locode or 'no LOCODE'})")
                if dest_mismatch is True:
                    warnings.append(f"Destination mismatch: carrier matched '{matched_dest}' vs requested '{res_dest_name}' ({res_dest_locode or 'no LOCODE'})")
                mismatch_warning = "⚠️ " + "; ".join(warnings)
            elif orig_mismatch is False and dest_mismatch is False:
                has_port_mismatch = False
                mismatch_warning = None
            else:
                has_port_mismatch = None  # UNKNOWN / Could Not Verify
                mismatch_warning = "Port match status: Could not verify (matched port string not returned by carrier)"

            db_result.raw_origin_input = request.origin
            db_result.raw_destination_input = request.destination
            db_result.resolved_origin_name = res_orig_name
            db_result.resolved_origin_locode = res_orig_locode
            db_result.resolved_destination_name = res_dest_name
            db_result.resolved_destination_locode = res_dest_locode
            db_result.submitted_origin = submitted_orig
            db_result.submitted_destination = submitted_dest
            db_result.matched_origin = matched_orig
            db_result.matched_destination = matched_dest
            db_result.has_port_mismatch = has_port_mismatch
            db_result.mismatch_warning = mismatch_warning

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
                    validity_till=q.validity_till,
                    free_time=q.free_time,
                    demurrage=q.demurrage,
                    detention=q.detention,
                    raw_data_json={
                        "source": q.source, 
                        "ref": q.raw_reference,
                        "routing": q.routing,
                        "free_time": q.free_time,
                        "demurrage": q.demurrage,
                        "detention": q.detention
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
            print(f"[JOB] {carrier_code}: {final_status.value} — {len(all_quotes)} quote(s)")

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
        finally:
            if connector:
                try:
                    await connector.close()
                    print(f"[JOB] Successfully closed connector browser for {carrier_code}")
                except Exception as ce:
                    print(f"[JOB] Error closing connector browser for {carrier_code}: {ce}")


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

        running_statuses = {"QUEUED", "RUNNING", "WAITING_FOR_HUMAN_VERIFICATION", "MANUAL_ACTION_REQUIRED"}
        all_done = all(
            s not in running_statuses and not (s.startswith("RUNNING") if s else False)
            for s in statuses
        )
        search_str_id = str(search_id)
        current_t = asyncio.current_task()
        is_task_running = search_str_id in active_search_tasks and any(
            t != current_t and not t.done() for t in active_search_tasks.get(search_str_id, [])
        )

        if not all_done or is_task_running:
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

        # Limit concurrent browser instances to prevent resource exhaustion and anti-bot triggers.
        # Default 7 so all selected carriers (Maersk, ONE, CMA, Hapag, MSC, OOCL, GreenX) launch browsers;
        # tune via CARRIER_MAX_CONCURRENCY if host RAM/CPU is constrained.
        import os
        max_concurrency = int(os.getenv("CARRIER_MAX_CONCURRENCY", "7"))
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
            await asyncio.shield(update_search_status(search_id))

    except BaseException as e:
        print(f"[JOB] run_all_carrier_searches was interrupted or cancelled: {e}")
        
        async def do_cleanup():
            async with get_async_session_maker()() as session:
                from sqlalchemy import or_
                # Mark all carrier results that are still QUEUED or RUNNING as FAILED
                results = (await session.execute(
                    select(CarrierSearchResult).where(
                        CarrierSearchResult.search_id == search_id,
                        or_(
                            CarrierSearchResult.status.in_(["QUEUED", "RUNNING"]),
                            CarrierSearchResult.status.like("RUNNING%")
                        )
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
    finally:
        # Guarantee queue lock is released the moment scraping completes or fails
        await queue_manager.release_lock(search_str_id)




async def cancel_all_active_searches():
    """Cancel all active search tasks."""
    cancelled_count = 0
    for search_id, tasks in list(active_search_tasks.items()):
        for task in tasks:
            if not task.done():
                task.cancel()
                cancelled_count += 1
    active_search_tasks.clear()
    return cancelled_count


async def run_vertical_batch_searches(
    batch_search_ids: list[UUID],
    carriers: list[str],
    requests: list[RateSearchRequest],
):
    """
    Executes multi-route RFQ tenders using Vertical Carrier-First Persistent Sessions.
    Dispatches 7 parallel persistent carrier workers, one per selected carrier.
    Each carrier worker launches Chromium ONCE, logs in ONCE, and searches all routes sequentially.
    """
    import os
    print(f"[VERTICAL BATCH] Starting vertical persistent batch for {len(requests)} routes across {len(carriers)} carriers...")
    
    # 1. Sort carriers (Hapag & ONE first)
    slow_carriers = ["HAPAG_LLOYD", "ONE"]
    sorted_carriers = sorted(carriers, key=lambda c: 0 if c.upper() in slow_carriers else 1)

    # Limit concurrent persistent carrier sessions (default 3 at a time) to keep CPU & RAM smooth
    max_concurrency = int(os.getenv("CARRIER_MAX_CONCURRENCY", "3"))
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_carrier_batch(carrier_code: str):
        async with semaphore:
            connector = get_connector(carrier_code)
            if not connector:
                print(f"[VERTICAL BATCH] No connector for {carrier_code}")
                return

            print(f"[VERTICAL BATCH] [{carrier_code}] Persistent Session Started (Concurrency limit={max_concurrency})")

            async def route_progress_callback(idx: int, req: RateSearchRequest, status: CarrierResultStatus, quotes: list[QuoteSchema]):
                # Find matching search_id for this route index
                if idx < len(batch_search_ids):
                    s_id = batch_search_ids[idx]
                    async with get_async_session_maker()() as session:
                        db_result = (await session.execute(
                            select(CarrierSearchResult).where(
                                CarrierSearchResult.search_id == s_id,
                                CarrierSearchResult.carrier == carrier_code
                            )
                        )).scalar_one_or_none()
                        if db_result:
                            db_result.status = status.value
                            db_result.completed_at = datetime.utcnow()
                            # Save quotes
                            for q_schema in quotes:
                                db_quote = Quote(
                                    carrier_result_id=db_result.id,
                                    etd=q_schema.etd,
                                    eta=q_schema.eta,
                                    transit_time_days=q_schema.transit_time_days,
                                    service_name=q_schema.service_name,
                                    vessel=q_schema.vessel,
                                    container_type=q_schema.container_type,
                                    container_quantity=q_schema.container_quantity,
                                    currency=q_schema.currency,
                                    basic_ocean_freight=q_schema.basic_ocean_freight,
                                    discount=q_schema.discount,
                                    final_freight_value=q_schema.final_freight_value,
                                    validity_till=q_schema.validity_till,
                                    raw_data_json={"routing": q_schema.routing, "free_time": q_schema.free_time}
                                )
                                session.add(db_quote)
                            await session.commit()

                        # Update main search status
                        await asyncio.shield(update_search_status(s_id))

            await connector.run_batch_persistent_search(requests, route_callback=route_progress_callback)

    active_tasks = [asyncio.create_task(run_carrier_batch(c)) for c in sorted_carriers]
    results = await asyncio.gather(*active_tasks, return_exceptions=True)
    for c, res in zip(sorted_carriers, results):
        if isinstance(res, Exception):
            print(f"[VERTICAL BATCH] Error executing batch for carrier {c}: {res}")
