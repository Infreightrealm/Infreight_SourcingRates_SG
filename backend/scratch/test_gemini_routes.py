import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
api_key = os.getenv("GEMINI_API_KEY")

async def test_bearer():
    print(f"API Key: {api_key} (len: {len(api_key) if api_key else 0})")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {"contents": [{"parts": [{"text": "Hello"}]}]}

    async with httpx.AsyncClient() as client:
        print("\n--- Testing Combo 5: Authorization: Bearer AQ.Ab8... ---")
        r = await client.post(url, json=payload, headers=headers)
        print("Status:", r.status_code)
        print("Response:", r.text[:300])

if __name__ == "__main__":
    asyncio.run(test_bearer())
