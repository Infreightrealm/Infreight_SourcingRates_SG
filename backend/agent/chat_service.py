"""
Chat Service — manages conversational AI queries from the frontend user using native Gemini 2.5 Flash API with intelligent local fallback.
"""
import os
import httpx
from sqlalchemy import select
from models.database import get_async_session_maker
from models.rate_search import RateSearch, CarrierSearchResult

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_INSTRUCTION = """You are the Infreight Logistics Rate Search Assistant, an internal AI helper for the Infreight Ocean & Air Carrier Rate Automation system.

Your job is to assist office employees and administrators in Singapore, Vietnam, and Malaysia with ocean and air freight rate queries, search status updates, and troubleshooting.

Key context about the system:
1. It uses Playwright automated browsers (connectors) to log in and scrape quotes from Maersk, ONE, CMA CGM, Hapag-Lloyd, OOCL, MSC, and GreenX.
2. VNC is enabled, allowing live browser viewing. If a bot challenge/CAPTCHA appears, the system pauses and requests manual solving in the VNC tab.
3. It has an AI-assisted self-healing layer that automatically catches selector failures, captures screenshots/DOM, and suggests selector fixes.
4. For Air Freight RFQs, it classifies mode as AIR and generates dual draft emails to Glenn (AWOT) and Jing Hui (ASPAC).
5. If the user asks about active or recent search statuses, you can use the search context provided below.

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
    Sends the chat message and history to native Gemini 2.5 Flash API.
    If Gemini API fails or returns error, gracefully falls back to local intelligent helper.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    search_context = await get_recent_search_status_context()

    if not api_key:
        print("[Chat Service] GEMINI_API_KEY is missing. Using local intelligent helper.")
        return _local_chatbot_fallback(message, search_context)

    full_instruction = f"{SYSTEM_INSTRUCTION}\n\n[Live System Status Context]:\n{search_context}"

    gemini_contents = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        gemini_contents.append({
            "role": role,
            "parts": [{"text": msg.get("content", "")}]
        })
        
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

    # Try 1: Direct x-goog-api-key header
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GEMINI_API_URL,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

            # Try 2: ?key= query parameter fallback
            url_with_key = f"{GEMINI_API_URL}?key={api_key}"
            response2 = await client.post(url_with_key, json=payload, headers={"Content-Type": "application/json"})
            if response2.status_code == 200:
                data2 = response2.json()
                return data2["candidates"][0]["content"]["parts"][0]["text"]

            print(f"[Chat Service] Gemini API returned error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Chat Service] Request failed: {e}")

    # Fallback to local intelligent assistant if API is unreachable
    return _local_chatbot_fallback(message, search_context)


def _local_chatbot_fallback(message: str, search_context: str) -> str:
    """Intelligent responder for search status, carrier guidance, air/sea info, and system help."""
    msg = message.lower()
    
    if any(k in msg for k in ["status", "recent", "search", "progress"]):
        return f"Here is the status of the most recent rate search:\n\n{search_context}"

    if any(k in msg for k in ["air", "airfreight", "glenn", "jing hui", "awot", "aspac"]):
        return "✈️ **Air Freight Support**: When you paste an Air RFQ into the Front Door, the system automatically extracts POL, POD, dimensions, and dangerous goods compliance, generating two competing draft emails for **Glenn (AWOT)** and **Jing Hui (ASPAC)**."
        
    if any(k in msg for k in ["hello", "hi", "hey", "good morning", "good day"]):
        return "Hi! I am your Infreight AI Assistant. I can help report recent rate search statuses, explain carrier connectors, or guide you through Air and Ocean RFQ automation!"
        
    if any(k in msg for k in ["captcha", "verification", "vnc", "puzzle"]):
        return "If a carrier site asks for verification (e.g. Cloudflare / DataDome / CAPTCHA), the browser pauses and sets status to `WAITING_FOR_HUMAN_VERIFICATION`. Open the live VNC panel in the dashboard, solve the puzzle manually, and the crawler will resume automatically!"
        
    if any(k in msg for k in ["carrier", "maersk", "one", "hapag", "cma", "oocl", "greenx", "msc"]):
        return "We support 7 major carriers: Maersk, ONE, CMA CGM, Hapag-Lloyd, OOCL, MSC, and GreenX. Searches process concurrently in batches of 3 workers to prevent rate limits."

    return f"I am your Infreight AI Assistant! Ask me about recent search status, carrier portal actions, or how Air & Ocean RFQ automation works.\n\n[Current Search Status]:\n{search_context}"
