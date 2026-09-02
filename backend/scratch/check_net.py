import urllib.request
import urllib.error
import socket
import os

def test_conn():
    print("Testing DNS resolution for www.cma-cgm.com...")
    try:
        ip = socket.gethostbyname("www.cma-cgm.com")
        print(f"DNS OK: www.cma-cgm.com resolved to {ip}")
    except Exception as e:
        print(f"DNS FAIL: {e}")

    print("\nTesting HTTP request to www.cma-cgm.com without proxy...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request("https://www.cma-cgm.com", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"HTTP OK: Status code {response.getcode()}")
    except urllib.error.URLError as e:
        print(f"HTTP FAIL (URLError): {e}")
    except Exception as e:
        print(f"HTTP FAIL: {e}")

if __name__ == "__main__":
    test_conn()
