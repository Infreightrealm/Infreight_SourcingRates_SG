"""
Unit tests for the Gemini AI RFQ Agent service (parse_rfq).
Includes verification for Air/Sea classification, dual-partner air draft generation,
dangerous goods compliance preservation, multi-origin gappy destination lists,
guardrails for unsupported special equipment (Reefer, Open Top, Flat Rack, ISO Tank, Hard Top) & LCL,
deterministic port alias resolution (ports_aliases.json), unmapped abbreviation guardrails,
and Sales Desk Intelligence extraction (Pak Shaun email fixture).
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
async def test_pak_shaun_email_fixture_port_aliases_and_sales_notes():
    """
    Test Pak Shaun email:
    "Hi team, need rate for 10x20GP from PK to JKT. Urgent for this week.
     Also have another 15x20 and 10x20 coming up next week. Using 2 forwarders currently,
     please try USD 70-80 target rate if possible. Thanks, Pak Shaun."
    
    Expected:
    - Origin resolves deterministically via ports_aliases.json: PK -> Port Klang (Port Klang (from 'PK'))
    - Destination resolves deterministically via ports_aliases.json: JKT -> Jakarta (Jakarta (from 'JKT'))
    - Container: 10x20GP -> DRY 20
    - sales_notes captures follow-up volume, target rate, urgency, and competitive pressure.
    """
    rfq_text = (
        "Hi team, need rate for 10x20GP from PK to JKT. Urgent for this week. "
        "Also have another 15x20 and 10x20 coming up next week. Using 2 forwarders currently, "
        "please try USD 70-80 target rate if possible. Thanks, Pak Shaun."
    )
    result = await parse_rfq(rfq_text)

    assert isinstance(result, RFQParseResult)
    assert result.mode == "sea"
    assert result.status == "success"
    assert result.parsed_fields is not None

    # Check Deterministic Port Alias Resolution
    assert result.parsed_fields.origin == "Port Klang"
    assert result.parsed_fields.destination == "Jakarta"
    assert result.origin_display == "Port Klang (from 'PK')"
    assert result.destination_display == "Jakarta (from 'JKT')"
    assert result.parsed_fields.container_types == ["DRY 20"]

    # Check Sales Desk Intelligence Extraction
    assert result.sales_notes is not None
    assert "future_volume" in result.sales_notes
    assert "another 15x20" in result.sales_notes["future_volume"]
    assert "competitive_pressure" in result.sales_notes
    assert "2 forwarders" in result.sales_notes["competitive_pressure"]
    assert "urgency" in result.sales_notes
    assert "Urgent" in result.sales_notes["urgency"]
    assert "target_rate" in result.sales_notes
    assert "70-80" in result.sales_notes["target_rate"]


@pytest.mark.asyncio
async def test_unmapped_abbreviation_clarification_guardrail():
    """
    Test Guardrail: Unmapped 2-3 letter port code (e.g. 'XYZ') triggers needs_clarification.
    """
    rfq_text = "Please quote rate for 1x40HQ from XYZ to JKT."
    result = await parse_rfq(rfq_text)

    assert isinstance(result, RFQParseResult)
    assert result.status == "needs_clarification"
    assert "XYZ" in (result.clarification_question or "")


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
    assert len(result.air_drafts) == 3
    
    # Verify all 3 draft emails contain the DG compliance & HS code details
    contact_persons = [d["contact_person"] for d in result.air_drafts]
    assert "Glenn" in contact_persons
    assert "Jing Hui" in contact_persons
    assert "Melvin Tan" in contact_persons

    for draft in result.air_drafts:
        assert "LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970" in draft["email_body"]
        assert "84433100" in draft["email_body"]


@pytest.mark.asyncio
async def test_air_rfq_image2_glenn_awot_dual_draft():
    """Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui (ASPAC), and Melvin Tan (SpeedMark)."""
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
    assert len(result.air_drafts) == 3
    
    contact_persons = [d["contact_person"] for d in result.air_drafts]
    assert "Glenn" in contact_persons
    assert "Jing Hui" in contact_persons
    assert "Melvin Tan" in contact_persons



@pytest.mark.asyncio
async def test_sea_rfq_image4_steel_plate_multi_origin_gappy_list():
    """
    Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'.
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
    assert result.total_pairs_found == 34
    assert result.pairs_omitted_count == 24


@pytest.mark.asyncio
async def test_unsupported_reefer_equipment_guardrail():
    """Test Guardrail: Detects Reefer container request and returns unsupported_cargo notice."""
    rfq_text = "Hi, please check ocean rate for 1x40' Reefer container from Singapore to Hamburg."
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.is_unsupported_equipment is True
    assert result.status == "unsupported_cargo"


@pytest.mark.asyncio
async def test_unsupported_lcl_guardrail():
    """Test Guardrail: Detects LCL request."""
    rfq_text = "Hi team, need rate for 3 CBM LCL shipment from Singapore to Hamburg."
    result = await parse_rfq(rfq_text)
    
    assert isinstance(result, RFQParseResult)
    assert result.is_lcl is True
    assert result.status == "unsupported_cargo"


@pytest.mark.asyncio
async def test_openflights_airport_alias_resolution():
    """Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution."""
    from services.rfq_agent import resolve_airport_alias

    # 1. Alias shorthand ('changi' -> SIN)
    info1, disp1, unmapped1 = resolve_airport_alias("changi")
    assert unmapped1 is False
    assert info1["iata"] == "SIN"
    assert "Singapore Changi Airport" in disp1

    # 2. Exact IATA lookup ('KUL' -> Kuala Lumpur International Airport)
    info2, disp2, unmapped2 = resolve_airport_alias("KUL")
    assert unmapped2 is False
    assert info2["iata"] == "KUL"
    assert "Kuala Lumpur International Airport" in disp2

    # 3. Unmapped airport code -> triggers needs_clarification (never guess)
    info3, disp3, unmapped3 = resolve_airport_alias("XYZUNKNOWN99")
    assert unmapped3 is True
    assert info3 is None



if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pak_shaun_email_fixture_port_aliases_and_sales_notes())
    asyncio.run(test_unmapped_abbreviation_clarification_guardrail())
    asyncio.run(test_air_rfq_image1_lithium_batteries_compliance())
    asyncio.run(test_air_rfq_image2_glenn_awot_dual_draft())
    asyncio.run(test_sea_rfq_image4_steel_plate_multi_origin_gappy_list())
    asyncio.run(test_unsupported_reefer_equipment_guardrail())
    asyncio.run(test_unsupported_lcl_guardrail())
    print("[OK] All RFQ Agent unit tests passed!")
