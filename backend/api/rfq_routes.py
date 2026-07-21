"""
API routes for RFQ parsing agent.
"""
from fastapi import APIRouter, HTTPException, status
from models.schemas import RFQParseRequest, RFQParseResult
from services.rfq_agent import parse_rfq

router = APIRouter(prefix="/api/rfq", tags=["RFQ Agent"])


@router.post("/parse", response_model=RFQParseResult)
async def parse_rfq_endpoint(payload: RFQParseRequest):
    """
    Parse a free-text RFQ email or message into a structured RateSearchRequest object
    or return a clarification question if required fields are missing/ambiguous.
    """
    try:
        result = await parse_rfq(raw_text=payload.text or "", image_b64=payload.image_b64, image_mime=payload.image_mime)
        return result

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
