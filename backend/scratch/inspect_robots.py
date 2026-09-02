import httpx
try:
    r = httpx.get("https://www.maersk.com/robots.txt", timeout=10.0)
    print(r.text)
except Exception as e:
    print(f"Failed to fetch robots.txt: {e}")
