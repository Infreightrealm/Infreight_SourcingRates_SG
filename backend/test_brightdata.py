"""
Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP API.
Uses only Python's built-in urllib module (zero external dependencies).
"""
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("BRIGHTDATA_API_KEY", "3df96956-7ddd-4a84-816e-0c015dc0069e")
ZONE = os.getenv("BRIGHTDATA_ZONE", "cma_cgm_unlocker")


def test_brightdata_api():
    print("[BRIGHTDATA] Testing Web Access HTTP API...")
    print(f"[BRIGHTDATA] Using Zone: '{ZONE}'")
    print(f"[BRIGHTDATA] Using API Key: '{API_KEY[:6]}...{API_KEY[-6:]}'")
    
    api_url = "https://api.brightdata.com/request"
    target_url = "https://www.cma-cgm.com/ebusiness/pricing/instant-Quoting"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "zone": ZONE,
        "url": target_url,
        "format": "raw"
    }
    
    print(f"[BRIGHTDATA] Sending POST request to Bright Data for URL: {target_url}")
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            print(f"[BRIGHTDATA] Response Status Code: {status_code}")
            
            if status_code == 200:
                print("[BRIGHTDATA] SUCCESS! Bypassed verification page.")
                html_content = response.read().decode("utf-8")
                print(f"[BRIGHTDATA] Retrieved HTML length: {len(html_content)} bytes")
                print(f"[BRIGHTDATA] Page Title from HTML: '{get_title(html_content)}'")
                
                # Save a snapshot of the fetched page to verify
                output_file = "brightdata_response.html"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"[BRIGHTDATA] Saved raw HTML page response to: {output_file}")
            else:
                print(f"[BRIGHTDATA] ❌ FAILED! Status Code: {status_code}")
                
    except urllib.error.HTTPError as e:
        print(f"[BRIGHTDATA] ❌ HTTP Error Code: {e.code}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"[BRIGHTDATA] Response Body: {error_body}")
        except Exception:
            pass
    except Exception as e:
        print(f"[BRIGHTDATA] Request Error: {e}")


def get_title(html: str) -> str:
    try:
        start = html.find("<title>") + len("<title>")
        end = html.find("</title>")
        if start != -1 and end != -1:
            return html[start:end].strip()
    except Exception:
        pass
    return "Unknown"


if __name__ == "__main__":
    test_brightdata_api()
