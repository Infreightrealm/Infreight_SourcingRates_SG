"""
Failure Detector — parses and structures error context from failed Playwright steps.
"""
from playwright.async_api import Page

def capture_failure_context(
    carrier: str,
    step_name: str,
    page: Page,
    error: Exception,
    original_selector: str = None,
    expected_action: str = None
) -> dict:
    """
    Assembles a standardized diagnostic dictionary containing all available details
    about the failed step, url, selectors, and the exception.
    """
    error_msg = str(error)
    current_url = page.url
    
    # Try to extract the selector from Playwright error message if not explicitly provided
    parsed_selector = original_selector
    if not parsed_selector:
        # Example playwright error: "Locator.click: Timeout 10000ms exceeded.\n  waiting for locator("button:has-text(\"GetQuote\")")"
        import re
        match = re.search(r"waiting for locator\(([\"'])(.*?)\1\)", error_msg, re.IGNORECASE)
        if match:
            parsed_selector = match.group(2)
            
    context = {
        "carrier": carrier.upper(),
        "step_name": step_name,
        "url": current_url,
        "original_selector": parsed_selector or "unknown_selector",
        "error_message": error_msg,
        "expected_action": expected_action or f"Execute action on step: {step_name}"
    }
    
    print(f"[Failure Detector] Captured failure on {context['carrier']} - Step: {step_name}, Selector: {context['original_selector']}")
    return context
