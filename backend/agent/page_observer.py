"""
Page Observer — captures page state (screenshot, DOM, visible text) on failure.
"""
import os
import datetime
from playwright.async_api import Page

# Base diagnostics directory inside the backend folder
DIAGNOSTICS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "diagnostics"
)

async def capture_page_state(page: Page, carrier: str, step_name: str) -> dict:
    """
    Captures screenshot, DOM HTML, and inner text of the current page.
    Saves everything under backend/diagnostics/<carrier>_<step_name>_<timestamp>/
    Returns a dictionary of saved file paths.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{carrier.lower()}_{step_name.lower()}_{timestamp}"
    session_dir = os.path.join(DIAGNOSTICS_DIR, folder_name)
    
    # Create the folder
    os.makedirs(session_dir, exist_ok=True)
    
    screenshot_path = os.path.join(session_dir, "screenshot.png")
    dom_path = os.path.join(session_dir, "dom.html")
    text_path = os.path.join(session_dir, "text.txt")
    
    results = {
        "diagnostics_dir": session_dir,
        "screenshot": None,
        "dom": None,
        "text": None
    }
    
    # 1. Capture Screenshot
    try:
        await page.screenshot(path=screenshot_path, full_page=False)
        results["screenshot"] = screenshot_path
    except Exception as se:
        print(f"[Observer] Failed to capture screenshot: {se}")
        
    # 2. Capture DOM
    try:
        dom_content = await page.content()
        with open(dom_path, "w", encoding="utf-8") as f:
            f.write(dom_content)
        results["dom"] = dom_path
    except Exception as de:
        print(f"[Observer] Failed to capture DOM: {de}")
        
    # 3. Capture Visible Text
    try:
        body_locator = page.locator("body")
        if await body_locator.is_attached():
            body_text = await body_locator.inner_text()
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(body_text)
            results["text"] = text_path
    except Exception as te:
        print(f"[Observer] Failed to capture page text: {te}")
        
    print(f"[Observer] Captured failure state for {carrier} (step: {step_name}) in {session_dir}")
    return results
