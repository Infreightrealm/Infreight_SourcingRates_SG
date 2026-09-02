import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carriers.one_connector import ONEConnector
from models.schemas import RateSearchRequest

async def test_one():
    # Set credentials if not already in env
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
        origin="SGSIN",        # Singapore
        destination="MYPKG",   # Port Klang
        container_type="DRY 20",  # 20 GP
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="Furniture",
        departure_date="today",
        carriers=["ONE"]
    )

    print("Searching quotes for Singapore to Port Klang...")
    status = await connector.search_quotes(request)
    print(f"Search status: {status}")

    print("Extracting quotes...")
    quotes = await connector.extract_quote_list()
    print(f"Extracted quotes: {len(quotes)}")
    for q in quotes:
        print(q)

    await connector.close()

if __name__ == "__main__":
    asyncio.run(test_one())
