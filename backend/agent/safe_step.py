"""
Safe Step — Playwright action execution wrapper with manual intervention pause and AI repair trigger.
"""
import inspect
from playwright.async_api import Page

from models.schemas import CarrierResultStatus
from models.database import get_async_session_maker
from sqlalchemy import update
from models.rate_search import CarrierSearchResult

from agent.manual_action_detector import detect_manual_action_required
from agent.failure_detector import capture_failure_context
from agent.page_observer import capture_page_state
from agent.selector_memory import get_approved_selector
from agent.ai_repair_agent import suggest_fix
from agent.repair_report import generate_report

async def update_carrier_status(search_id_str: str, carrier: str, status: CarrierResultStatus, error_msg: str = None):
    """Updates the status of a carrier search in the database."""
    if not search_id_str:
        return
    try:
        from uuid import UUID
        search_id = UUID(search_id_str)
        async with get_async_session_maker()() as session:
            stmt = (
                update(CarrierSearchResult)
                .where(
                    CarrierSearchResult.search_id == search_id,
                    CarrierSearchResult.carrier == carrier.upper()
                )
                .values(
                    status=status.value,
                    error_message=error_msg
                )
            )
            await session.execute(stmt)
            await session.commit()
            print(f"[Safe Step] Updated DB status for {carrier.upper()} to {status.value}")
    except Exception as e:
        print(f"[Safe Step] Database status update failed: {e}")

async def safe_step(
    step_name: str,
    carrier: str,
    page: Page,
    expected_action: str,
    action
):
    """
    Executes a Playwright action. 
    If it fails:
      1. Detects CAPTCHA/bot challenges and pauses for manual interaction.
      2. Checks selector memory for approved fixes and applies them.
      3. If no approved fix exists, calls AI to generate a suggestion and saves a repair report.
    """
    search_id_str = getattr(page, "search_id", None)
    
    # 1. Check if there is an already approved selector in memory
    original_selector = None
    # Deduce original selector from trace/arguments if possible
    approved_selector = get_approved_selector(carrier, step_name, original_selector)
    
    if approved_selector:
        print(f"[Safe Step] Using approved fallback selector from memory: '{approved_selector}'")
        try:
            # Try to execute the action using the approved selector
            sig = inspect.signature(action)
            if len(sig.parameters) > 0:
                return await action(approved_selector)
            else:
                # Default fallback action: click
                loc = page.locator(approved_selector).first
                await loc.wait_for(state="visible", timeout=5000)
                await loc.click(force=True)
                return True
        except Exception as memory_err:
            print(f"[Safe Step] Approved memory selector failed, falling back to original: {memory_err}")

    # 2. Try running the original action
    try:
        sig = inspect.signature(action)
        if len(sig.parameters) > 0:
            return await action()
        else:
            return await action()
    except Exception as error:
        print(f"[Safe Step] Step '{step_name}' failed: {error}")
        
        # 3. Check for Bot Challenge / CAPTCHA (Manual Intervention required)
        if await detect_manual_action_required(page):
            print(f"[Safe Step] Bot challenge detected on {carrier} for step '{step_name}'. Entering VNC pause...")
            # Update status to MANUAL_ACTION_REQUIRED in DB
            await update_carrier_status(search_id_str, carrier, CarrierResultStatus.MANUAL_ACTION_REQUIRED, "Human verification is required. Please solve the challenge in the VNC tab.")
            
            # Polling loop: Wait for human to solve it
            for attempt in range(120): # 120 seconds timeout
                await page.wait_for_timeout(1000)
                if not await detect_manual_action_required(page):
                    print("[Safe Step] Manual challenge cleared by user. Resuming automation...")
                    # Update status back to RUNNING
                    await update_carrier_status(search_id_str, carrier, CarrierResultStatus.RUNNING)
                    try:
                        # Re-run original action
                        if len(sig.parameters) > 0:
                            return await action()
                        else:
                            return await action()
                    except Exception as retry_err:
                        print(f"[Safe Step] Retry failed after manual challenge clear: {retry_err}")
                        error = retry_err
                        break
            else:
                # Polling timed out
                print("[Safe Step] Timed out waiting for human verification in VNC.")
                await update_carrier_status(search_id_str, carrier, CarrierResultStatus.TIMEOUT, "Verification timeout.")
                raise error

        # 4. Normal Selector Failure -> Trigger observer and AI repair flow
        # Gathers metadata context
        context = capture_failure_context(
            carrier=carrier,
            step_name=step_name,
            page=page,
            error=error,
            expected_action=expected_action
        )
        
        # Capture screenshot, DOM snapshot, and text
        observer_results = await capture_page_state(page, carrier, step_name)
        
        # Update DB status to CONNECTOR_REPAIR_REQUIRED
        await update_carrier_status(
            search_id_str, 
            carrier, 
            CarrierResultStatus.CONNECTOR_REPAIR_REQUIRED,
            f"Layout change detected. Analyzing replacement locators..."
        )
        
        # Query Gemini AI for repair suggestion
        repair_suggestion = await suggest_fix(context, observer_results.get("dom"))
        
        # Generate repair report
        report = generate_report(context, observer_results, repair_suggestion)
        
        # Update DB status to AI_SELECTOR_REPAIR_SUGGESTED
        await update_carrier_status(
            search_id_str,
            carrier,
            CarrierResultStatus.AI_SELECTOR_REPAIR_SUGGESTED,
            f"AI Repair suggested: '{repair_suggestion.get('suggested_selector')}'"
        )
        
        # Raise failure to halt crawler run so developer/admin can review
        raise Exception(f"AI Selector Repair Suggested: {repair_suggestion.get('suggested_selector')}. Reason: {repair_suggestion.get('reasoning')}")
