import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from carriers.hapag_lloyd_connector import HapagLloydConnector

async def test():
    c = HapagLloydConnector()
    # No need to login just to test the suggestions API, it uses Playwright but we can just check what the API returns if we mock it, wait _get_location_suggestions uses playwright page.
    # Actually I can just look at hapag_lloyd_connector.py to see what it does.
    pass

if __name__ == "__main__":
    asyncio.run(test())
