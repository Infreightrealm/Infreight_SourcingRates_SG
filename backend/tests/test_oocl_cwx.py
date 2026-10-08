import pytest
from carriers.oocl_connector import OOCLConnector
from models.schemas import RateSearchRequest

@pytest.mark.asyncio
async def test_oocl_cwx_heavy_weight_charge_applied():
    conn = OOCLConnector()
    
    # 20GP with 25000kg (>= 21000kg) -> CWX should be applied ($250)
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
        "dialog_charges": {"20GP": {"EBS": 295.0}}
    }
    q1 = await conn.normalize_result(dict(raw_quote), [], request=req_20gp_heavy)
    assert any(c.name == "CWX 20' Heavy Weight Charge" and c.amount == 250.0 for c in q1.included_freight_surcharges)
    assert q1.final_freight_value == 2975.0 + 295.0 + 250.0


@pytest.mark.asyncio
async def test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold():
    conn = OOCLConnector()
    
    # 20GP with 20000kg (< 21000kg) -> CWX should NOT be applied
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
        "dialog_charges": {"20GP": {"EBS": 295.0}}
    }
    q2 = await conn.normalize_result(dict(raw_quote), [], request=req_20gp_light)
    assert not any("CWX" in c.name for c in q2.included_freight_surcharges)
    assert q2.final_freight_value == 2975.0 + 295.0


@pytest.mark.asyncio
async def test_oocl_cwx_heavy_weight_charge_not_applied_40gp():
    conn = OOCLConnector()
    
    # 40GP with 25000kg -> CWX only applies to 20'
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
        "dialog_charges": {"40GP": {"EBS": 295.0}}
    }
    q3 = await conn.normalize_result(dict(raw_quote_40), [], request=req_40gp_heavy)
    assert not any("CWX" in c.name for c in q3.included_freight_surcharges)
    assert q3.final_freight_value == 4000.0 + 295.0
