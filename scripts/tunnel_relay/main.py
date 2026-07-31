import os
import uuid
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Infreight Railway Tunnel Relay")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client_ws: WebSocket = None
pending_requests: dict[str, asyncio.Future] = {}
SECRET_TOKEN = os.getenv("TUNNEL_SECRET_TOKEN", "InfreightSecretTunnel2026")

@app.get("/health")
async def health(request: Request):
    global client_ws
    if not client_ws:
        return Response(
            content='{"status": "unhealthy", "error": "Local tunnel client is not connected", "local_client_connected": false}',
            status_code=503,
            media_type="application/json"
        )
    
    # Forward health check directly to local backend http://localhost:8000/health
    req_id = str(uuid.uuid4())
    payload = {
        "req_id": req_id,
        "method": "GET",
        "path": "/health",
        "query": "",
        "headers": {},
        "body": ""
    }
    
    fut = asyncio.get_event_loop().create_future()
    pending_requests[req_id] = fut
    
    try:
        await client_ws.send_json(payload)
        res_data = await asyncio.wait_for(fut, timeout=3.0)
        status_code = res_data.get("status_code", 503)
        res_body = res_data.get("body", "").encode("latin1")
        if status_code == 200:
            return Response(content=res_body, status_code=200, media_type="application/json")
        else:
            return Response(content='{"status": "unhealthy", "error": "Local backend returned non-200 on /health"}', status_code=503, media_type="application/json")
    except Exception:
        pending_requests.pop(req_id, None)
        return Response(content='{"status": "unhealthy", "error": "Local backend /health timed out or local server not running"}', status_code=503, media_type="application/json")

@app.websocket("/tunnel/ws")
async def websocket_endpoint(websocket: WebSocket):
    global client_ws
    token = websocket.query_params.get("token")
    if token != SECRET_TOKEN:
        await websocket.close(code=4001, reason="Unauthorized token")
        return
        
    await websocket.accept()
    client_ws = websocket
    print("[Tunnel Relay] Local Laptop Client connected successfully!")
    
    try:
        while True:
            msg = await websocket.receive_json()
            req_id = msg.get("req_id")
            if req_id and req_id in pending_requests:
                fut = pending_requests.pop(req_id)
                if not fut.done():
                    fut.set_result(msg)
    except WebSocketDisconnect:
        print("[Tunnel Relay] Local Laptop Client disconnected.")
    finally:
        if client_ws == websocket:
            client_ws = None

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def relay_request(request: Request, path: str):
    global client_ws
    if request.method == "OPTIONS":
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        })
        
    if not client_ws:
        return Response(
            content='{"error": "Local backend client is not connected to Railway tunnel relay. Please run run_tunnel_client.bat on your computer."}',
            status_code=503,
            media_type="application/json"
        )
    
    req_id = str(uuid.uuid4())
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    payload = {
        "req_id": req_id,
        "method": request.method,
        "path": f"/{path}",
        "query": str(request.query_params),
        "headers": headers,
        "body": body.decode("latin1") if body else ""
    }
    
    fut = asyncio.get_event_loop().create_future()
    pending_requests[req_id] = fut
    
    try:
        await client_ws.send_json(payload)
        res_data = await asyncio.wait_for(fut, timeout=180.0)
        
        status_code = res_data.get("status_code", 200)
        res_headers = res_data.get("headers", {})
        res_body = res_data.get("body", "").encode("latin1")
        
        for h in ["content-encoding", "transfer-encoding", "content-length"]:
            res_headers.pop(h, None)
            
        res_headers["Access-Control-Allow-Origin"] = "*"
        return Response(content=res_body, status_code=status_code, headers=res_headers)
    except asyncio.TimeoutError:
        pending_requests.pop(req_id, None)
        return Response(content='{"error": "Local backend request timed out"}', status_code=504, media_type="application/json")
    except Exception as e:
        pending_requests.pop(req_id, None)
        return Response(content=f'{{"error": "Tunnel relay error: {str(e)}"}}', status_code=500, media_type="application/json")
