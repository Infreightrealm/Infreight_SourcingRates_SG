import pytest
from carriers.one_connector import ONEConnector


def test_one_free_time_parser_test_a():
    text = """ONE QUOTE Free Time Information
Origin
Demurrage 6 Days
Detention 5 Days
Destination
Combined DEM & DET 14 Days*
*ONE QUOTE Special Free Time
For details, refer to ONE Standard Tariff"""
    res = ONEConnector._parse_free_time_text(text)
    assert res["free_time"] == 14
    assert res["demurrage"] is None
    assert res["detention"] is None
    assert res["mode"] == "combined"


def test_one_free_time_parser_test_b():
    text = "Destination Combined DEM & DET 10 Days"
    res = ONEConnector._parse_free_time_text(text)
    assert res["free_time"] == 10
    assert res["demurrage"] is None
    assert res["detention"] is None
    assert res["mode"] == "combined"


def test_one_free_time_parser_test_c():
    text = "Destination Demurrage: 6 Days Detention: 5 Days"
    res = ONEConnector._parse_free_time_text(text)
    assert res["free_time"] == 11
    assert res["demurrage"] == 6
    assert res["detention"] == 5
    assert res["mode"] == "split"


def test_one_free_time_parser_origin_only_ignored():
    text = "Origin Demurrage 6 Days Detention 5 Days"
    res = ONEConnector._parse_free_time_text(text)
    assert res["free_time"] is None
    assert res["demurrage"] is None
    assert res["detention"] is None
    assert res["mode"] is None
