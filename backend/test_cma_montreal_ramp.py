"""
CMA CGM Montreal Ramp selection test.
Verifies that when destination_delivery_type="RAMP" (or prefer_ramp=True),
CMA CGM connector selects the 'MONTREAL, QC (CAMTR) · CANADA RAMP . DOOR' option
from the dropdown instead of the PORT option.
"""
import os
import asyncio

# Clear proxy vars
for key in ["CMA_PROXY_USER", "CMA_PROXY_PASS", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS",
            "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

from carriers.cma_connector import CMAConnector
from models.schemas import RateSearchRequest

from dotenv import load_dotenv
load_dotenv()

async def test_montreal_ramp():
    print("Initializing CMAConnector...")
    connector = CMAConnector()

    try:
        print("Logging in to CMA CGM...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
        if not login_success:
            print("Login failed, aborting.")
            return

        request = RateSearchRequest(
            origin="CNSHA",
            destination="Montreal [CAMTR]",
            destination_delivery_type="RAMP",
            prefer_ramp=True,
            container_type="DRY 40H",
            container_quantity=1,
            weight_per_container_kg=15000,
            commodity="Furniture",
            departure_date="tomorrow",
            carriers=["CMA"]
        )

        print(f"Testing search_quotes with prefer_ramp={request.prefer_ramp}, delivery_type={request.destination_delivery_type}...")
        status = await connector.search_quotes(request)
        print(f"search_quotes status: {status}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_montreal_ramp())
