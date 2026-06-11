import asyncio
from models.schemas import RateSearchRequest
from carriers.maersk_connector import MaerskConnector

async def run_test():
    print("Starting Maersk test...")
    req = RateSearchRequest(
        origin="Singapore",
        destination="Hamburg",
        container_type="40' General Purpose",
        commodity="Furniture",
        carriers=["MAERSK"]
    )
    connector = MaerskConnector()
    print("Searching...")
    status, quotes = await connector.run_full_search(req)
    print(f"Search status: {status}")
    print(f"Found {len(quotes)} quotes.")
    for q in quotes:
        print("-------")
        print(f"ETD: {q.etd}, ETA: {q.eta}")
        print(f"Routing: {q.routing}")
        print(f"Price: {q.final_freight_value}")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(run_test())
