from fastapi import APIRouter, Query
from typing import List, Optional
from services.port_manager import suggest_ports, search_port, get_port_by_code

router = APIRouter(prefix="/api/ports", tags=["Ports"])

@router.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2), limit: int = 5):
    """Get port suggestions for autocomplete."""
    suggestions = suggest_ports(q, limit=limit)
    return suggestions

@router.get("/search")
async def search(q: str = Query(..., min_length=2), country: Optional[str] = None):
    """Full port search."""
    results = search_port(q, country=country)
    return results

@router.get("/{code}")
async def get_port(code: str):
    """Get specific port details by UN/LOCODE."""
    port = get_port_by_code(code)
    return port
