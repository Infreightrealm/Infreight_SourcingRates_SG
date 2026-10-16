from datetime import date
import pytest
from carriers.oocl_connector import OOCLConnector
from models.schemas import RateSearchRequest, CarrierResultStatus


def test_oocl_fs_pair_and_select_2nd_window_fallback():
    """
    Test that when OOCL FreightSmart finds a sailing in week 3 (e.g. day 18, 2026-11-03 from 2026-10-16)
    because no sailings exist in the initial 14-day window (e.g. Singapore -> Brisbane):
    _fs_pair_and_select does NOT drop all quotes, but falls back to the 28-day horizon (2nd window).
    """
    fs_rows = [
        {
            "kind": "E-Spot",
            "etd": "2026-11-03",
            "total_price": 3245.0,
            "prices": {"DRY 20": 3245.0, "DRY 40": 3740.0, "DRY 40H": 3740.0},
            "vessel": "EVER GRADE",
            "free_time": 14,
        }
    ]

    # With default 14-day search window from 2026-10-16:
    res = OOCLConnector._fs_pair_and_select(
        fs_rows, [],
        today=date(2026, 10, 16),
        window_days=14
    )

    # Must preserve the 3 container quotes (DRY 20, DRY 40, DRY 40H) instead of dropping them
    assert len(res) == 3
    assert all(r["etd"] == "2026-11-03" for r in res)
    types = {r["container_type"] for r in res}
    assert types == {"DRY 20", "DRY 40", "DRY 40H"}


def test_oocl_fs_pair_and_select_active_date_preservation():
    """
    Test that when FreightSmart extracts the active date as fallback (even if beyond 28 days),
    _fs_pair_and_select preserves it rather than returning an empty list that causes false NO_QUOTES_AVAILABLE.
    """
    fs_rows = [
        {
            "kind": "E-Spot",
            "etd": "2026-12-01",  # > 28 days
            "total_price": 2800.0,
            "prices": {"DRY 20": 2800.0},
            "vessel": "OOCL ROTTERDAM",
        }
    ]

    res = OOCLConnector._fs_pair_and_select(
        fs_rows, [],
        today=date(2026, 10, 16),
        window_days=14
    )

    assert len(res) == 1
    assert res[0]["etd"] == "2026-12-01"


def test_oocl_filter_cheapest_in_14d_window_picks_2nd_window():
    """
    Test that filter_cheapest_in_14d_window selects the 2nd window card when 1st window is empty.
    """
    conn = OOCLConnector()
    cards = [
        {
            "etd": "2026-11-03",
            "total_price": 3245.0,
            "prices": {"DRY 20": 3245.0},
            "container_type": "DRY 20"
        }
    ]

    # departure_date: 2026-10-16. Nov 3 is day 18 -> 2nd window.
    filtered = conn.filter_cheapest_in_14d_window(cards, "2026-10-16")
    assert len(filtered) == 1
    assert filtered[0]["etd"] == "2026-11-03"


def test_oocl_serve_for_cycle_matches_container():
    conn = OOCLConnector()
    from models.schemas import QuoteSchema
    conn._cached_quotes = [
        QuoteSchema(
            container_type="DRY 20",
            final_freight_value=3245.0,
            basic_ocean_freight=3245.0,
            etd="2026-11-03",
            source="OOCL"
        ),
        QuoteSchema(
            container_type="DRY 40H",
            final_freight_value=3740.0,
            basic_ocean_freight=3740.0,
            etd="2026-11-03",
            source="OOCL"
        ),
    ]

    req_20 = RateSearchRequest(origin_code="SGSIN", destination_code="AUBNE", container_type="20GP", carriers=["OOCL"])
    q_20 = conn._serve_for_cycle(req_20)
    assert len(q_20) == 1
    assert q_20[0].final_freight_value == 3245.0

    req_40h = RateSearchRequest(origin_code="SGSIN", destination_code="AUBNE", container_type="40HQ", carriers=["OOCL"])
    q_40h = conn._serve_for_cycle(req_40h)
    assert len(q_40h) == 1
    assert q_40h[0].final_freight_value == 3740.0


def test_oocl_connector_has_get_booking_start_date():
    conn = OOCLConnector()
    assert hasattr(conn, "get_booking_start_date")
    assert callable(conn.get_booking_start_date)

    d_iso = conn.get_booking_start_date("2026-11-13")
    assert d_iso == date(2026, 11, 13)

    d_today = conn.get_booking_start_date("today")
    assert d_today == date.today()

    d_none = conn.get_booking_start_date(None)
    assert d_none == date.today()

