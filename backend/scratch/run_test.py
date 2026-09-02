import asyncio
import os
import sys

# Add parent directory to path so it can import from models and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_connector import ONEConnector
from models.schemas import RateSearchRequest

async def test_one():
    if not os.getenv("ONE_USERNAME"):
        os.environ["ONE_USERNAME"] = "INFREIGHTSG"
    if not os.getenv("ONE_PASSWORD"):
        os.environ["ONE_PASSWORD"] = "IFSGa2020"

    print("Initializing ONEConnector...")
    connector = ONEConnector()
    
    print("Logging in...")
    login_success = await connector.login()
    if not login_success:
        print("Login failed.")
        await connector.close()
        return

    request = RateSearchRequest(
        origin="Shanghai",
        destination="Los Angeles",
        container_type="40'HC",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="FAK",
        departure_date="today",
        carriers=["ONE"]
    )

    print("Searching quotes...")
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
