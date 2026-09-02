import os
import sys
import asyncio
import re

# Add backend directory to python path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from carriers.cma_connector import CMAConnector
from models.schemas import RateSearchRequest

async def main():
    os.environ["CMA_USERNAME"] = "bookingsg@in-freight.com"
    os.environ["CMA_PASSWORD"] = "@IFSGc2023"
    
    # Clear proxy env vars
    for key in ["CMA_PROXY_USER", "CMA_PROXY_PASS", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS",
                "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
        os.environ[key] = ""

    print("Initializing CMAConnector...")
    connector = CMAConnector()
    try:
        print("Logging in...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
        if not login_success:
            return

        request = RateSearchRequest(
            origin="SGSIN",
            destination="KHKOS",
            container_type="DRY 40H",
            container_quantity=1,
            weight_per_container_kg=15000,
            commodity="Furniture",
            departure_date="tomorrow",
            carriers=["CMA"]
        )

        print("Searching quotes for SGSIN to KHKOS...")
        status = await connector.search_quotes(request)
        print(f"Search status: {status}")

        if status.value == "AVAILABLE_QUOTES_FOUND":
            # Count the quote cards visible initially
            cards_sel = 'article.card-route-horizontal, article[class*="card-route-horizontal"], div[class*="schedules-result"], div[class*="sailing-result"]'
            cards = connector.page.locator(cards_sel)
            initial_count = await cards.count()
            print(f"Initially found {initial_count} cards.")
            
            # Print card contents initially
            for idx in range(initial_count):
                txt = await cards.nth(idx).inner_text()
                print(f"Initial Card {idx}:\n{txt[:200]}\n{'-'*30}")
            
            # Load more
            print("Running _handle_more_results()...")
            await connector._handle_more_results()
            
            # Count again
            cards = connector.page.locator(cards_sel)
            total_count = await cards.count()
            print(f"After loading more, found {total_count} cards.")
            
            # Extract and print all quotes parsed
            raw_quotes = await connector.extract_quote_list()
            print(f"Extracted {len(raw_quotes)} quotes from quote list.")
            
            for idx, q in enumerate(raw_quotes):
                print(f"Quote {idx}: ETD={q['etd']} | ETA={q['eta']} | Transit={q['transit_time_days']} | Vessel={q['vessel']} | Price={q['total_price']}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
