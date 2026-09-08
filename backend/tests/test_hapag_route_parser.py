# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

def test_hapag_port_to_port_hamburg():
    connector = HapagLloydConnector()
    connector.current_request = RateSearchRequest(
        origin="MYPGU",
        destination="Hamburg, Germany [DEHAM]",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=20000,
        departure_date="2026-09-20",
        carriers=["HAPAG_LLOYD"]
    )

    text = """
    Received at Terminal/Ramp (PoL)
    Pasir Gudang (MYPGU)
    Delivered to Terminal/Ramp (PoD)
    Hamburg (DEHAM)
    Estimated Transit Time 36 days
    """

    res = connector._parse_left_panel_route(text)
    assert res["pod"] == "Hamburg (DEHAM)"
    assert res["routing"] == "Direct"
    assert res["is_inland"] is False
    assert res["tt"] == 36
    assert ")" not in res["routing"]
    assert res["pod"] != ")"

def test_hapag_inland_winnipeg():
    connector = HapagLloydConnector()
    connector.current_request = RateSearchRequest(
        origin="MYPKG",
        destination="Winnipeg, MB",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=20000,
        departure_date="2026-09-20",
        carriers=["HAPAG_LLOYD"]
    )

    text = """
    Estimated Transit Time 49 days
    Received at Terminal/Ramp (PoL)
    Port Kelang
    + 2 more
    PoD
    Vancouver, BC
    Delivered to Terminal/Ramp
    Winnipeg, MB
    """

    res = connector._parse_left_panel_route(text)
    assert res["pod"] == "Vancouver, BC"
    assert res["routing"] == "Vancouver, BC"
    assert res["is_inland"] is True
    assert res["tt"] == 49
    assert res["has_transshipment"] is True

def test_hapag_sanitize_brackets():
    connector = HapagLloydConnector()
    # If text is somehow degenerate
    assert connector._sanitize_route_value(")") is None
    assert connector._sanitize_route_value(")", default="Direct") == "Direct"
    assert connector._sanitize_route_value("(", default="Direct") == "Direct"
    assert connector._sanitize_route_value("[]", default="Direct") == "Direct"
    assert connector._sanitize_route_value("Hamburg (DEHAM)") == "Hamburg (DEHAM)"
    assert connector._sanitize_route_value("Vancouver, BC") == "Vancouver, BC"

@pytest.mark.asyncio
async def test_hapag_normalize_result_no_bracket_leak():
    connector = HapagLloydConnector()
    connector.current_request = RateSearchRequest(
        origin="MYPGU",
        destination="Hamburg, Germany [DEHAM]",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=20000,
        departure_date="2026-09-20",
        carriers=["HAPAG_LLOYD"]
    )
    connector._last_parsed_pod = "Hamburg (DEHAM)"
    connector._last_parsed_routing = "Direct"

    raw_quote = {
        "index": 0,
        "etd": "2026-09-20",
        "eta": "2026-10-26",
        "transit_time_days": 36,
        "total_price": 1500.0,
        "raw_date": "2026-09-20",
        "port_of_discharge": ")",  # Simulate corrupt raw input
        "routing": ")"              # Simulate corrupt raw input
    }
    charges = [{
        "name": "Ocean Freight",
        "amount": 1500.0,
        "currency": "USD",
        "container_type": "DRY 20",
        "category": "BASIC_OCEAN_FREIGHT"
    }]

    quote = await connector.normalize_result(raw_quote, charges, container_type="DRY 20", is_sold_out=False)
    # Both must be cleaned of brackets and fallback safely
    assert quote.port_of_discharge == "Hamburg (DEHAM)"
    assert quote.routing == "Direct"
    assert quote.port_of_discharge != ")"
    assert quote.routing != ")"

