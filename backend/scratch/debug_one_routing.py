import asyncio
import os
import sys

# Reconfigure stdout to UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

async def run_debug():
    if not os.getenv("ONE_USERNAME"):
        os.environ["ONE_USERNAME"] = "INFREIGHTSG"
    if not os.getenv("ONE_PASSWORD"):
        os.environ["ONE_PASSWORD"] = "IFSGa2020"

    print("Initializing ONEConnector...")
    connector = ONEConnector()
    
    print("Logging in...")
    login_success = await connector.login()
    print(f"Login success: {login_success}")
    if not login_success:
        await connector.close()
        return

    request = RateSearchRequest(
        origin="SGSIN",
        destination="SAJED",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="Furniture",
        departure_date="today",
        carriers=["ONE"]
    )

    # Search
    print("Searching quotes...")
    status = await connector.search_quotes(request)
    print(f"Search status: {status}")

    # Extract list
    print("Extracting quotes...")
    quotes = await connector.extract_quote_list()
    print(f"Extracted quotes: {len(quotes)}")
    
    if quotes:
        first_quote = quotes[0]
        print("First quote details:")
        print(first_quote)
        
        # Open price breakdown (this clicks Details)
        print("Opening price breakdown...")
        opened = await connector.open_price_breakdown(first_quote)
        print(f"Breakdown opened: {opened}")
        
        # Take a screenshot
        artifact_dir = r"C:\Users\Brian\.gemini\antigravity\brain\2febadc4-254a-470f-9d04-a43202bfc8dc"
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_breakdown_expanded.png"))
        
        # Dump the inner text and HTML of the body
        body_text = await connector.page.locator("body").inner_text()
        body_html = await connector.page.locator("body").inner_html()
        with open(os.path.join(artifact_dir, "one_body_text.txt"), "w", encoding="utf-8") as f:
            f.write(body_text)
        with open(os.path.join(artifact_dir, "one_body_html.html"), "w", encoding="utf-8") as f:
            f.write(body_html)
        print("Saved body text and HTML to brain directory.")
        # Run extraction
        print("Running extract_charge_breakdown...")
        charges = await connector.extract_charge_breakdown()
        print(f"Extracted {len(charges)} charges.")
        print(f"Extracted routing: {connector.current_routing}")
        
        # Normalize
        normalized = await connector.normalize_result(first_quote, charges)
        print(f"Normalized routing: {normalized.routing}")
        print(f"Normalized free time: {normalized.free_time}")
        print(f"Normalized quote schema: {normalized}")
            
    # Always take a screenshot of the final page state for debugging
    try:
        artifact_dir = r"C:\Users\Brian\.gemini\antigravity\brain\2febadc4-254a-470f-9d04-a43202bfc8dc"
        await connector.page.screenshot(path=os.path.join(artifact_dir, "one_search_result_final.png"))
        print("Captured final page screenshot one_search_result_final.png")
    except Exception as e:
        print(f"Failed to capture final screenshot: {e}")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
