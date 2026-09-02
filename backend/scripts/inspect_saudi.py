import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from carriers.hapag_lloyd_connector import HapagLloydConnector

async def check():
    connector = HapagLloydConnector()
    await connector.login()
    await connector.page.goto("https://www.hapag-lloyd.com/en/online-business/quotation/detention-demurrage/middle-east.html")
    await connector.page.wait_for_timeout(3000)
    
    links = await connector.page.locator('a[href*=".pdf"]').all()
    for link in links:
        t = await link.inner_text()
        h = await link.get_attribute('href')
        print(f"TEXT: {t} | HREF: {h}")
            
    await connector.close()

if __name__ == "__main__":
    asyncio.run(check())
