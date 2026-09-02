import asyncio
from models.schemas import RateSearchRequest
from carriers.oocl_connector import OOCLConnector

async def main():
    req = RateSearchRequest(
        origin="Shanghai",
        destination="Rotterdam",
        container_type="DRY 20",
        commodity="FAK",
        carriers=["OOCL"]
    )
    conn = OOCLConnector()
    status = await conn.search_quotes(req)
    print(status)
    quotes = await conn.extract_quote_list()
    print(f"Extracted {len(quotes)} quotes")
    await conn.close()

asyncio.run(main())
