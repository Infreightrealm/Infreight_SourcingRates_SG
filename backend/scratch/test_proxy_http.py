import os
import httpx
from dotenv import load_dotenv

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

proxy_user = os.getenv("MAERSK_PROXY_USER")
proxy_pass = os.getenv("MAERSK_PROXY_PASS")

print(f"Proxy User: {proxy_user}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

def test_port(port):
    print(f"\n--- Testing HTTPX proxy on port {port} fetching Maersk with browser headers ---")
    proxy_url = f"http://{proxy_user}:{proxy_pass}@brd.superproxy.io:{port}"
    
    try:
        with httpx.Client(proxy=proxy_url, timeout=20.0, verify=False) as client:
            r = client.get("https://www.maersk.com/login", headers=headers)
            print(f"Status: {r.status_code}")
            print(f"Content Length: {len(r.text)} bytes")
            if "Forbidden" in r.text or "Access Denied" in r.text:
                print("Content contains block message!")
            else:
                print("Page loaded successfully without text blocks!")
    except Exception as e:
        print(f"Failed: {e}")

test_port(22225)
test_port(33335)
