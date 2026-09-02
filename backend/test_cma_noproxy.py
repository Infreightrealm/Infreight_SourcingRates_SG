"""Quick CMA test with ALL proxy env vars forcibly cleared BEFORE any import triggers load_dotenv()."""
import os
# Force-clear ALL proxy env vars BEFORE any module import can call load_dotenv()
for key in ["CMA_PROXY_USER", "CMA_PROXY_PASS", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS",
            "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

# Now import (which triggers load_dotenv via database.py, but override=True won't override existing)
import asyncio
from carriers.cma_connector import CMAConnector
from models.schemas import RateSearchRequest

async def test_cma():
    os.environ["CMA_USERNAME"] = "bookingsg@in-freight.com"
    os.environ["CMA_PASSWORD"] = "@IFSGc2023"

    # Double-check proxy is truly off
    print(f"CMA_PROXY_USER = {repr(os.getenv('CMA_PROXY_USER'))}")
    print(f"MAERSK_PROXY_USER = {repr(os.getenv('MAERSK_PROXY_USER'))}")

    connector = CMAConnector()
    try:
        print("Logging in (NO PROXY, real Chrome)...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_cma())
