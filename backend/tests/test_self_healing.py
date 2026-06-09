"""
Self-Healing Layer & Chatbot Test Suite.
Tests the selector memory, failure detector, observer, repair agent, safe_step, and chatbot service.
"""
import os
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent.selector_memory import get_approved_selector, save_approved_selector, reject_selector
from agent.failure_detector import capture_failure_context
from agent.manual_action_detector import detect_manual_action_required
from agent.ai_repair_agent import suggest_fix
from agent.chat_service import handle_chat_query
from agent.safe_step import safe_step

@pytest.fixture(autouse=True)
def clean_selector_memory():
    """Wipes the selector memory JSON file before and after each test."""
    from agent.selector_memory import MEMORY_FILE_PATH
    if os.path.exists(MEMORY_FILE_PATH):
        try:
            os.remove(MEMORY_FILE_PATH)
        except Exception:
            pass
    yield
    if os.path.exists(MEMORY_FILE_PATH):
        try:
            os.remove(MEMORY_FILE_PATH)
        except Exception:
            pass

def test_selector_memory():
    # Save approved selector
    save_approved_selector("ONE", "click_submit", "button[type='submit']", "button:has-text('Submit')")
    
    # Check approved selector
    approved = get_approved_selector("ONE", "click_submit", "button[type='submit']")
    assert approved == "button:has-text('Submit')"
    
    # Reject selector
    reject_selector("ONE", "click_submit")
    assert get_approved_selector("ONE", "click_submit", "button[type='submit']") is None

@pytest.mark.asyncio
async def test_manual_action_detector_captcha():
    # Test case: CAPTCHA iframe is present
    mock_locator = MagicMock()
    mock_locator.is_visible = AsyncMock(return_value=True)
    
    mock_page = MagicMock()
    mock_page.locator.return_value.first = mock_locator
    mock_page.frames = []
    
    # Should detect CAPTCHA selector
    is_challenge = await detect_manual_action_required(mock_page)
    assert is_challenge is True

@pytest.mark.asyncio
async def test_manual_action_detector_text():
    # Test case: CAPTCHA text on page
    mock_locator = MagicMock()
    mock_locator.is_visible = AsyncMock(return_value=False)
    
    mock_body = MagicMock()
    mock_body.is_attached = AsyncMock(return_value=True)
    mock_body.inner_text = AsyncMock(return_value="Please verify you are a human before accessing CMA CGM.")
    
    mock_page = MagicMock()
    mock_page.locator.side_effect = lambda sel: mock_body if sel == "body" else mock_locator
    mock_page.frames = []
    
    # Should detect CAPTCHA text
    is_challenge = await detect_manual_action_required(mock_page)
    assert is_challenge is True

def test_failure_detector():
    mock_page = MagicMock()
    mock_page.url = "https://www.one-line.com/booking"
    
    error = Exception("Timeout 30000ms exceeded.\nWaiting for locator(\"button:has-text('GetQuote')\")")
    
    context = capture_failure_context(
        carrier="ONE",
        step_name="click_submit",
        page=mock_page,
        error=error,
        original_selector=None,
        expected_action="Click search button"
    )
    
    assert context["carrier"] == "ONE"
    assert context["original_selector"] == "button:has-text('GetQuote')"
    assert "Timeout 30000ms" in context["error_message"]
    assert context["url"] == "https://www.one-line.com/booking"

@pytest.mark.asyncio
async def test_ai_repair_agent_offline_fallback():
    context = {
        "carrier": "ONE",
        "step_name": "click_get_quote",
        "original_selector": "button:has-text('Get Quote')",
        "expected_action": "Click submit button to search quotes",
        "url": "https://www.one-line.com/rates",
        "error_message": "Timeout exceeded"
    }
    
    # HTML containing alternative button label
    mock_dom = """
    <html>
      <body>
        <form>
          <button type="submit">View Quote</button>
        </form>
      </body>
    </html>
    """
    
    temp_dom_file = "temp_test_dom.html"
    with open(temp_dom_file, "w", encoding="utf-8") as f:
        f.write(mock_dom)
        
    try:
        # Should fall back to local text-heuristic rules
        with patch.dict(os.environ, {}, clear=True):
            result = await suggest_fix(context, temp_dom_file)
            
            assert "suggested_selector" in result
            assert "reasoning" in result
            assert result["suggested_selector"] == 'button:has-text("View Quote")'
            assert result["risk_level"] == "MEDIUM"
    finally:
        if os.path.exists(temp_dom_file):
            os.remove(temp_dom_file)

@pytest.mark.asyncio
async def test_chat_service_offline_fallback():
    # Verify local helper responds without API key
    with patch.dict(os.environ, {}, clear=True):
        reply = await handle_chat_query("How do I solve CAPTCHAs?", [])
        assert "WAITING_FOR_HUMAN_VERIFICATION" in reply or "VNC" in reply
        
        reply_status = await handle_chat_query("status", [])
        assert "status" in reply_status.lower() or "recent" in reply_status.lower()

@pytest.mark.asyncio
async def test_safe_step_success():
    mock_action = AsyncMock(return_value="ActionSucceeded")
    mock_page = MagicMock()
    mock_page.search_id = "test-search-id"
    
    res = await safe_step(
        step_name="click_button",
        carrier="ONE",
        page=mock_page,
        expected_action="Click normal button",
        action=mock_action
    )
    
    assert res == "ActionSucceeded"
    mock_action.assert_called_once()
