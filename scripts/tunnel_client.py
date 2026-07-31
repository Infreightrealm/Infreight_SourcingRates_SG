import os
import sys
import json
import asyncio
import argparse

try:
    import httpx
    import websockets
except ImportError:
    print("[ERROR] Required packages 'httpx' or 'websockets' not found.")
    print("Installing requirements...")
    os.system(f"{sys.executable} -m pip install httpx websockets")
    import httpx
    import websockets

DEFAULT_RELAY_URL = "wss://infreight-tunnel-production.up.railway.app/tunnel/ws?token=InfreightSecretTunnel2026"
DEFAULT_LOCAL_BACKEND = "http://localhost:8000"

async def handle_request(ws, req_data, http_client: httpx.AsyncClient):
    req_id = req_data["req_id"]
    method = req_data["method"]
    path = req_data["path"]
    query = req_data.get("query", "")
    headers = req_data.get("headers", {})
    body = req_data.get("body", "").encode("latin1")
    
    url = f"{LOCAL_BACKEND_URL}{path}"
    if query:
        url += f"?{query}"
        
    try:
        res = await http_client.request(
            method=method,
            url=url,
            headers=headers,
            content=body,
            timeout=180.0
        )
        response_payload = {
            "req_id": req_id,
            "status_code": res.status_code,
            "headers": dict(res.headers),
            "body": res.content.decode("latin1")
        }
    except Exception as e:
        print(f"\n🔴 [ERROR] Could not reach local Python backend ({LOCAL_BACKEND_URL}{path}): {e}")
        print(f"👉 Make sure python main.py or run_server.py is RUNNING in another terminal window on your laptop!\n")
        response_payload = {
            "req_id": req_id,
            "status_code": 503,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": f"Local backend fetch failed: {str(e)}"})
        }
        
    try:
        await ws.send(json.dumps(response_payload))
    except Exception as e:
        print(f"[Client] Error sending response payload for {req_id}: {e}")

async def run_client(relay_url: str, local_backend: str):
    global LOCAL_BACKEND_URL
    LOCAL_BACKEND_URL = local_backend.rstrip("/")
    
    # Convert http/https URL to ws/wss if needed
    ws_url = relay_url.replace("http://", "ws://").replace("https://", "wss://")
    if "/tunnel/ws" not in ws_url:
        ws_url = ws_url.rstrip("/") + "/tunnel/ws?token=InfreightSecretTunnel2026"
        
    print(f"\n=======================================================")
    print(f"   Infreight Railway Cloud Tunnel Client")
    print(f"=======================================================")
    print(f"Target Local Backend: {LOCAL_BACKEND_URL}")
    print(f"Connecting to Railway Relay: {ws_url} ...\n")
    
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    async with httpx.AsyncClient(limits=limits) as http_client:
        while True:
            try:
                async with websockets.connect(ws_url, max_size=20_000_000, ping_interval=20, ping_timeout=20) as ws:
                    print("🟢 CONNECTED TO RAILWAY CLOUD!")
                    print(f"Traffic sent to Railway Cloud is now forwarded live to {LOCAL_BACKEND_URL}.\n")
                    
                    while True:
                        msg = await ws.recv()
                        req_data = json.loads(msg)
                        asyncio.create_task(handle_request(ws, req_data, http_client))
            except Exception as e:
                print(f"🟡 Connection lost ({e}). Reconnecting in 3 seconds...")
                await asyncio.sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infreight Railway Cloud Tunnel Client")
    parser.add_argument("--relay", default=DEFAULT_RELAY_URL, help="Railway Tunnel Relay WSS URL")
    parser.add_argument("--backend", default=DEFAULT_LOCAL_BACKEND, help="Local Backend URL")
    args = parser.parse_args()
    
    try:
        asyncio.run(run_client(args.relay, args.backend))
    except KeyboardInterrupt:
        print("\nTunnel Client stopped.")
