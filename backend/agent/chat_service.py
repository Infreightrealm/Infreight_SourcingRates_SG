"""
Chat Service — manages conversational AI queries from the frontend user.
"""
import os
import httpx
from sqlalchemy import select
from models.database import get_async_session_maker
from models.rate_search import RateSearch, CarrierSearchResult

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_INSTRUCTION = """You are the Infreight Logistics Rate Search Assistant, an internal AI helper for the Infreight Ocean Carrier Rate Automation system.

Your job is to assist office employees and administrators in Singapore, Vietnam, and Malaysia with ocean freight rate queries, search status updates, and troubleshooting.

Key context about the system:
1. It uses hardcoded Playwright automated browsers (connectors) to log in and scrape quotes from Maersk, ONE, CMA CGM, and Hapag-Lloyd.
2. VNC is enabled, allowing live browser viewing. If a bot challenge/CAPTCHA appears, the system pauses and requests manual solving in the VNC tab.
3. It has an AI-assisted self-healing layer that automatically catches selector failures, captures screenshots/DOM, and suggests selector fixes (which developers can approve).
4. If the user asks about active or recent search statuses, you can use the search context provided below.

Be professional, helpful, and concise. Explain things in a clear, non-evasive, user-friendly manner.
"""

async def get_recent_search_status_context() -> str:
    """Queries the database for the most recent rate search status to give the chatbot live context."""
    try:
        async with get_async_session_maker()() as session:
            stmt = select(RateSearch).order_by(RateSearch.created_at.desc()).limit(1)
            search = (await session.execute(stmt)).scalar_one_or_none()
            if not search:
                return "No searches have been run yet."
                
            res_stmt = select(CarrierSearchResult).where(CarrierSearchResult.search_id == search.id)
            results = (await session.execute(res_stmt)).scalars().all()
            
            lines = [
                f"Most Recent Search ID: {search.id}",
                f"Route: {search.origin} -> {search.destination}",
                f"Overall Search Status: {search.status}",
                "Carrier Results:"
            ]
            for r in results:
                err_part = f" (Error: {r.error_message})" if r.error_message else ""
                lines.append(f" - {r.carrier}: {r.status}{err_part}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving search context: {e}"

async def handle_chat_query(message: str, history: list[dict]) -> str:
    """
    Sends the chat message and history to Gemini API.
    Returns the AI assistant's response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    search_context = await get_recent_search_status_context()

    # 1. Fallback if API key is not configured
    if not api_key:
        print("[Chat Service] GEMINI_API_KEY is missing. Using local rule-based chatbot helper.")
        return _local_chatbot_fallback(message, search_context)

    # 2. Formulate prompt instruction with live search context
    full_instruction = f"{SYSTEM_INSTRUCTION}\n\n[Live System Status Context]:\n{search_context}"

    # 3. Format history for Gemini API (user -> user, assistant -> model)
    gemini_contents = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        gemini_contents.append({
            "role": role,
            "parts": [{"text": msg.get("content", "")}]
        })
        
    # Append current message
    gemini_contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    payload = {
        "contents": gemini_contents,
        "systemInstruction": {
            "parts": [{"text": full_instruction}]
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={api_key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return reply
            else:
                print(f"[Chat Service] Gemini API returned error {response.status_code}: {response.text}")
                return "I'm having trouble connecting to my brain service right now. Please verify your GEMINI_API_KEY is valid."
    except Exception as e:
        print(f"[Chat Service] Request failed: {e}")
        return "I encountered a connection error while trying to process your query. Please try again in a moment."


def _local_chatbot_fallback(message: str, search_context: str) -> str:
    """A rule-based responder for local setups where no Gemini key is set."""
    msg = message.lower()
    
    if "status" in msg or "recent" in msg or "search" in msg:
        return f"Here is the status of the most recent rate search:\n\n{search_context}\n\n*(Note: To enable full AI chat features, please configure a GEMINI_API_KEY in your server variables)*"
        
    if "hello" in msg or "hi" in msg:
        return "Hello! I am your local Infreight Assistant. I can help report search status or explain carrier portal actions. Since GEMINI_API_KEY is not set, I am running in local offline mode."
        
    if "captcha" in msg or "verification" in msg:
        return "If a carrier site asks for verification, the browser will pause and set the status to WAITING_FOR_HUMAN_VERIFICATION. You should open the VNC panel in the bottom right corner of the dashboard, solve the puzzle manually, and the crawler will resume automatically once cleared."
        
    return "I am running in offline mode because the GEMINI_API_KEY is not configured in the environment. I can report rate search status if you ask for 'status' or explain 'captcha' flows!"
