import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db, _get_session_maker
from sqlalchemy import text

async def check_db():
    print("=======================================================")
    print("   Testing Database Connection & Persistence")
    print("=======================================================")

    await init_db()
    session_maker = _get_session_maker()
    async with session_maker() as session:
        # Query total rate searches and carrier results
        res_searches = await session.execute(text("SELECT COUNT(*) FROM rate_searches"))
        total_searches = res_searches.scalar()
        
        res_carrier = await session.execute(text("SELECT COUNT(*) FROM carrier_search_results"))
        total_carrier_results = res_carrier.scalar()

        print(f"Total Rate Searches stored in DB: {total_searches}")
        print(f"Total Carrier Search Results stored in DB: {total_carrier_results}")

if __name__ == "__main__":
    asyncio.run(check_db())
