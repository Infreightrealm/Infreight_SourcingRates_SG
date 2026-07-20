"""
Unit tests for the Gemini AI RFQ Agent service (parse_rfq).
"""
import sys
import os
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Enable mock mode for pytest execution when no live key is present
os.environ["RFQ_AGENT_MOCK"] = "true"

from services.rfq_agent import parse_rfq
from models.schemas import RFQParseResult, RateSearchRequest


@pytest.mark.asyncio
async def test_complete_unambiguous_rfq_total_weight():
    """Test 1: Complete RFQ text with total weight calculation (18,000 kg total for 2 containers -> 9,000 kg/container)."""
    rfq_text = (
        "Hi team,\n"
        "Please quote rate from Shanghai to Rotterdam for 2x40HQ containers, "
        "weight 18,000 kg total for 2 containers, commodity Furniture. Target ETD 2026-08-15.\n"
        "Thanks!"
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.status == "success"
    assert result.parsed_fields is not None
    
    fields = result.parsed_fields
    assert fields.origin == "Shanghai"
    assert fields.destination == "Rotterdam"
    assert fields.container_quantity == 2
    assert fields.weight_per_container_kg == 9000.0  # 18000 / 2 = 9000 kg per container
    assert fields.commodity == "Furniture"
    assert "DRY 40H" in fields.container_types
    assert result.clarification_question is None
    assert "origin" in result.extracted_fields
    assert "destination" in result.extracted_fields
    assert "weight_per_container_kg" in result.extracted_fields
    assert result.debug_raw_llm_response is not None


@pytest.mark.asyncio
async def test_missing_field_requires_clarification():
    """Test 2: Missing required field (POD / destination) returns needs_clarification."""
    rfq_text = (
        "Hi Infreight, need rate for 1x20GP container loaded from Singapore. "
        "Weight is 15 MT. Please quote asap."
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.status == "needs_clarification"
    assert result.parsed_fields is None
    assert result.clarification_question is not None
    assert "destination" in result.missing_fields or "pod" in [m.lower() for m in result.missing_fields]


@pytest.mark.asyncio
async def test_relative_date_no_weight_fabrication():
    """Test 3: Relative date terms ('early August') resolve to date, and missing weight is NOT fabricated in extraction."""
    rfq_text = (
        "Good day, please check rate for 1x40HQ Electronics from Singapore to Hamburg. "
        "Departure scheduled for early August."
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.status == "success"
    assert result.parsed_fields is not None
    
    dep_date = result.parsed_fields.departure_date
    assert dep_date is not None
    parsed_date = datetime.strptime(dep_date, "%Y-%m-%d")
    assert parsed_date.month == 8
    assert 1 <= parsed_date.day <= 10

    # Weight was not in text -> marked as injected default, NOT extracted
    assert "weight_per_container_kg" in result.default_injected_fields
    assert "weight_per_container_kg" not in result.extracted_fields


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_complete_unambiguous_rfq_total_weight())
    asyncio.run(test_missing_field_requires_clarification())
    asyncio.run(test_relative_date_no_weight_fabrication())
    print("[OK] All Gemini RFQ Agent unit tests passed!")
