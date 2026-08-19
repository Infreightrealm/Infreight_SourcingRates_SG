import pytest
from carriers.maersk_connector import MaerskConnector
from models.schemas import RateSearchRequest

def test_maersk_single_container_type_configuration():
    connector = MaerskConnector()

    # Test case 1: Single container selection (20GP / DRY 20)
    req1 = RateSearchRequest(
        carriers=["MAERSK"],
        origin="Singapore",
        destination="Nhava Sheva",
        container_type="DRY 20",
        container_types=["DRY 20"],
        weight_per_container_kg=20000.0,
    )

    req_ctypes1 = getattr(req1, "container_types", None) or [getattr(req1, "container_type", "DRY 20")]
    target1 = []
    seen1 = set()
    for ct in req_ctypes1:
        m_name = connector._map_container_type(ct)
        if m_name not in seen1:
            target1.append((m_name, req1.weight_per_container_kg))
            seen1.add(m_name)

    assert len(target1) == 1, "Single container selection should result in exactly 1 container type on Maersk form"
    assert target1[0][0] == "20 Dry Standard", "DRY 20 should map to '20 Dry Standard'"

    # Test case 2: Dual container selection (DRY 20 & DRY 40H)
    req2 = RateSearchRequest(
        carriers=["MAERSK"],
        origin="Singapore",
        destination="Nhava Sheva",
        container_type="DRY 20",
        container_types=["DRY 20", "DRY 40H"],
        weight_per_container_kg=20000.0,
    )

    req_ctypes2 = getattr(req2, "container_types", None) or [getattr(req2, "container_type", "DRY 20")]
    target2 = []
    seen2 = set()
    for ct in req_ctypes2:
        m_name = connector._map_container_type(ct)
        if m_name not in seen2:
            target2.append((m_name, req2.weight_per_container_kg))
            seen2.add(m_name)

    assert len(target2) == 2
    assert target2[0][0] == "20 Dry Standard"
    assert target2[1][0] == "40 Dry High"
