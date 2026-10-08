import pytest
from carriers.oocl_connector import OOCLConnector
from models.schemas import RateSearchRequest

@pytest.mark.asyncio
async def test_oocl_cwx_port_pair_surabaya_karachi():
    conn = OOCLConnector()
    
    # Port Pair: IDSUB -> PKKHI (Surabaya -> Karachi): CWX is $250 when weight >= 21000kg
    req_20gp_heavy = RateSearchRequest(
        origin_code="IDSUB",
        destination_code="PKKHI",
        departure_date="2026-10-15",
        carriers=["OOCL"],
        container_type="20GP",
        weight_per_container_kg=25000.0
    )
    raw_quote = {
        "kind": "E-Spot",
        "basic_ocean_freight": 2975.0,
        "final_freight_value": 2975.0,
        "currency": "USD",
        "container_type": "20GP",
        "dialog_charges": {"20GP": {"EBS": 295.0, "CWX": 250.0}}
    }
    q1 = await conn.normalize_result(dict(raw_quote), [], request=req_20gp_heavy)
    assert any(c.name == "CWX 20' Heavy Weight Charge" and c.amount == 250.0 for c in q1.included_freight_surcharges)
    assert q1.final_freight_value == 2975.0 + 295.0 + 250.0


@pytest.mark.asyncio
async def test_oocl_cwx_different_port_pair_different_amount():
    conn = OOCLConnector()
    
    # Port Pair: CNNGB -> NLRTM (Ningbo -> Rotterdam): Carrier has CWX rate of $180 (different from $250)
    req = RateSearchRequest(
        origin_code="CNNGB",
        destination_code="NLRTM",
        departure_date="2026-10-20",
        carriers=["OOCL"],
        container_type="20GP",
        weight_per_container_kg=24000.0
    )
    raw_quote = {
        "kind": "E-Spot",
        "basic_ocean_freight": 1600.0,
        "final_freight_value": 1600.0,
        "currency": "USD",
        "container_type": "20GP",
        "dialog_charges": {
            "20GP": {
                "ETS": 45.0,
                "CWX": 180.0,
                "CWX_NAME": "20' Heavy Weight Charge - European Tier",
                "CWX_REASON": "20' Heavy Weight Charge (Weight: At or Above 18000.000 Net KG)"
            }
        }
    }
    q = await conn.normalize_result(dict(raw_quote), [], request=req)
    cwx_charge = next(c for c in q.included_freight_surcharges if "CWX" in c.name or "Heavy Weight" in c.name)
    # Must use this port pair's specific $180 rate, NOT hardcoded $250
    assert cwx_charge.amount == 180.0
    assert q.final_freight_value == 1600.0 + 45.0 + 180.0


@pytest.mark.asyncio
async def test_oocl_cwx_port_pair_without_cwx():
    conn = OOCLConnector()
    
    # Port Pair: SGSIN -> MYPKG (Singapore -> Port Klang): Carrier does NOT charge CWX on this route
    req = RateSearchRequest(
        origin_code="SGSIN",
        destination_code="MYPKG",
        departure_date="2026-10-18",
        carriers=["OOCL"],
        container_type="20GP",
        weight_per_container_kg=26000.0
    )
    raw_quote = {
        "kind": "E-Spot",
        "basic_ocean_freight": 350.0,
        "final_freight_value": 350.0,
        "currency": "USD",
        "container_type": "20GP",
        "dialog_charges": {"20GP": {"EBS": 30.0}}  # No CWX in modal table
    }
    q = await conn.normalize_result(dict(raw_quote), [], request=req)
    # Must NOT inject a false $250 surcharge when this port pair has no CWX
    assert not any("CWX" in c.name for c in q.included_freight_surcharges)
    assert q.final_freight_value == 350.0 + 30.0


@pytest.mark.asyncio
async def test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold():
    conn = OOCLConnector()
    
    # Weight below threshold (e.g. 20,000 KG < 21,000 KG): CWX should be $0
    req_20gp_light = RateSearchRequest(
        origin_code="IDSUB",
        destination_code="PKKHI",
        departure_date="2026-10-15",
        carriers=["OOCL"],
        container_type="20GP",
        weight_per_container_kg=20000.0
    )
    raw_quote = {
        "kind": "E-Spot",
        "basic_ocean_freight": 2975.0,
        "final_freight_value": 2975.0,
        "currency": "USD",
        "container_type": "20GP",
        "dialog_charges": {"20GP": {"EBS": 295.0, "CWX": 0.0}}
    }
    q2 = await conn.normalize_result(dict(raw_quote), [], request=req_20gp_light)
    assert not any("CWX" in c.name for c in q2.included_freight_surcharges)
    assert q2.final_freight_value == 2975.0 + 295.0


@pytest.mark.asyncio
async def test_oocl_cwx_heavy_weight_charge_not_applied_40gp():
    conn = OOCLConnector()
    
    # 40GP with 25000kg -> CWX only applies to 20' containers
    req_40gp_heavy = RateSearchRequest(
        origin_code="IDSUB",
        destination_code="PKKHI",
        departure_date="2026-10-15",
        carriers=["OOCL"],
        container_type="40GP",
        weight_per_container_kg=25000.0
    )
    raw_quote_40 = {
        "kind": "E-Spot",
        "basic_ocean_freight": 4000.0,
        "final_freight_value": 4000.0,
        "currency": "USD",
        "container_type": "40GP",
        "dialog_charges": {"40GP": {"EBS": 295.0, "CWX": 250.0}}
    }
    q3 = await conn.normalize_result(dict(raw_quote_40), [], request=req_40gp_heavy)
    assert not any("CWX" in c.name for c in q3.included_freight_surcharges)
    assert q3.final_freight_value == 4000.0 + 295.0
