import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.chat_service import handle_chat_query

async def main():
    print("Testing Chat Assistant with live GEMINI_API_KEY...")
    res = await handle_chat_query("hi", [])
    print("\nAssistant Response:")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
