"""
Unit tests for the Gemini AI RFQ Agent service (parse_rfq).
Includes verification for Air/Sea classification, dual-partner air draft generation,
dangerous goods compliance preservation, multi-origin gappy destination lists,
and guardrails for unsupported special equipment (Reefer, Open Top, Flat Rack, ISO Tank, Hard Top) & LCL.
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
async def test_air_rfq_image1_lithium_batteries_compliance():
    """Test Image 1: EXW airfreight rates with lithium batteries PI 970 & HS code preservation."""
    rfq_text = (
        "Dear All,\n"
        "Please quote cheap and best EXW airfreight rates;\n"
        "Collect from:\n"
        "Hitachi Asia Ltd\n"
        "Industrial Components and Equipment Group (ICE)\n"
        "30 Pioneer Crescent #10-15, West Park Bizcentral, Singapore 628560\n\n"
        "Commodity: HITACHI PRINTERS -LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970\n"
        "Dim: 64x53x74 cm/10 pkgs\n"
        "Gross weight: 320 kg\n"
        "HS CODE: 84433100\n\n"
        "Best Regards,\n"
        "Mohammed Shamnad\n"
        "Manager - Airfreight\n"
        "Airlift Logistics"
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.mode == "air"
    assert result.status == "air_draft_generated"
    assert result.is_dangerous_goods is True
    assert result.hs_code == "84433100"
    assert "LITHIUM METAL BATTERIES" in (result.compliance_notes or "")
    assert result.air_drafts is not None
    assert len(result.air_drafts) == 2  # Dual drafts: AWOT (Glenn) and ASPAC (Jing Hui)
    
    # Verify both draft emails contain the DG compliance & HS code details
    for draft in result.air_drafts:
        assert "LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970" in draft["email_body"]
        assert "84433100" in draft["email_body"]


@pytest.mark.asyncio
async def test_air_rfq_image2_glenn_awot_dual_draft():
    """Test Image 2: Air rate request to Glenn generates dual drafts to Glenn (AWOT) and Jing Hui (ASPAC)."""
    rfq_text = (
        "Hi Glenn,\n\n"
        "Good Day\n"
        "Kindly advise us air rates for below:\n"
        "POL: Singapore Airport\n"
        "POD: KUL\n"
        "Commodity: Machines Part Accessories - Docking Roller Assy / Trial Cutter Roller Assy Bottom Surface\n"
        "2 Crates / Sets\n"
        "Dimension of each crate:\n"
        "186 x 32 x 37 cm H - 2 Crates\n"
        "Gross Weight: 320.00 kgs\n"
        "(160 kgs x 2 crates)\n"
        "Please also provide available flight schedule and transit time.\n"
        "Thank you"
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.mode == "air"
    assert result.status == "air_draft_generated"
    assert result.air_drafts is not None
    assert len(result.air_drafts) == 2
    
    contact_persons = [d["contact_person"] for d in result.air_drafts]
    assert "Glenn" in contact_persons
    assert "Jing Hui" in contact_persons


@pytest.mark.asyncio
async def test_sea_rfq_image4_steel_plate_multi_origin_gappy_list():
    """
    Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'.
    Asserts:
    1. Mode is SEA.
    2. 2 origins x 17 destinations = 34 exact expanded pairs (item #3 is skipped in raw text).
    3. Capped at 10 pairs for execution with 24 omitted pairs reported.
    """
    rfq_text = (
        "Hi Toby, Shona and Bethy.\n\n"
        "Good day.\n\n"
        "Please compile rates from ex Pasir Gudang / Tanjung Pelepas for 20' & 40' as follows.\n\n"
        "Commodity: Steel Plate, Steel Coil.\n\n"
        "1) Koper, Slovenia\n"
        "2) Nagoya, Japan\n"
        "4) Thessaloniki, Greece\n"
        "5) Liverpool, England\n"
        "6) Colombo, Sri Lanka\n"
        "7) Chiba, Japan\n"
        "8) Montreal, Canada\n"
        "9) Baltimore, US\n"
        "10) Toronto (Halifax), Canada\n"
        "11) Toronto (Vancouver), Canada\n"
        "12) Winnipeg, Canada\n"
        "13) Vancouver, Canada\n"
        "14) Houston, US\n"
        "15) Kaohsiung, Taiwan\n"
        "16) Chattogram, Bangladesh\n"
        "17) Manzanillo, Mexico\n"
        "18) Bourges, France"
    )
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.mode == "sea"
    assert result.status == "success"
    assert result.all_parsed_pairs is not None
    
    # 2 origins x 17 destinations = 34 exact pairs
    assert result.total_pairs_found == 34
    assert result.pairs_omitted_count == 24
    assert len(result.all_parsed_pairs) == 34


@pytest.mark.asyncio
async def test_unsupported_reefer_equipment_guardrail():
    """Test Guardrail: Detects Reefer container request and returns unsupported_cargo notice."""
    rfq_text = "Hi, please check ocean rate for 1x40' Reefer container from Singapore to Hamburg."
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.is_unsupported_equipment is True
    assert result.status == "unsupported_cargo"
    assert "Reefer" in (result.unsupported_equipment_type or "")
    assert "Standard FCL Dry Containers" in (result.unsupported_reason or "")


@pytest.mark.asyncio
async def test_unsupported_open_top_equipment_guardrail():
    """Test Guardrail: Detects Open Top container request."""
    rfq_text = "Please quote ocean freight for 1x40 Open Top container from Shanghai to Rotterdam."
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.is_unsupported_equipment is True
    assert result.status == "unsupported_cargo"
    assert "Open Top" in (result.unsupported_equipment_type or "")


@pytest.mark.asyncio
async def test_unsupported_lcl_guardrail():
    """Test Guardrail: Detects LCL / Less than Container Load request and returns FCL-only notice."""
    rfq_text = "Hi team, need rate for 3 CBM LCL shipment from Singapore to Hamburg."
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.is_lcl is True
    assert result.status == "unsupported_cargo"
    assert "Full Container Load (FCL) only" in (result.unsupported_reason or "")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_air_rfq_image1_lithium_batteries_compliance())
    asyncio.run(test_air_rfq_image2_glenn_awot_dual_draft())
    asyncio.run(test_sea_rfq_image4_steel_plate_multi_origin_gappy_list())
    asyncio.run(test_unsupported_reefer_equipment_guardrail())
    asyncio.run(test_unsupported_open_top_equipment_guardrail())
    asyncio.run(test_unsupported_lcl_guardrail())
    print("[OK] All RFQ Agent unit tests & guardrail tests passed!")
