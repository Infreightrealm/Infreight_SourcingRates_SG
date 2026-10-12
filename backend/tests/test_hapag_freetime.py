"""Hapag-Lloyd destination free time: whole-word country matching on the table."""
import json
import os

from carriers.hapag_lloyd_api_connector import HapagLloydAPIConnector
from services.hapag_freetime import freetime_days, match_freetime_entry

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "hapag_freetime.json"), encoding="utf-8"))


def days(text, container="DRY 20"):
    hit = match_freetime_entry(CONFIG, text)
    return freetime_days(hit[1], container) if hit else None


def test_nigeria_is_not_matched_as_niger():
    assert days("Apapa, Nigeria [NGAPP]") == 7
    assert days("Niamey, Niger") == 21


def test_pakistan_has_its_own_entry():
    assert days("Karachi, Pakistan [PKKHI]") == 5


def test_longest_country_name_wins():
    assert match_freetime_entry(CONFIG, "Lae, Papua New Guinea")[0] == "Papua New Guinea"


def test_api_connector_uses_the_locode_country():
    c = HapagLloydAPIConnector()
    assert c._get_freetime_days("NGAPP", "Apapa", "DRY 20") == 7
    assert c._get_freetime_days("PKKHI", "Karachi", "DRY 40") == 5


def test_default_free_time_is_marked_estimated():
    c = HapagLloydAPIConnector()
    assert c._lookup_freetime("JOAQJ", "Al 'Aqabah, Jordan [JOAQJ]", "DRY 20") == (4, True)  # Jordan not in the table
    assert c._lookup_freetime("NGAPP", "Apapa", "DRY 20") == (7, False)
    assert c._lookup_freetime("USLAX", "Los Angeles", "DRY 40") == (4, False)  # set figure, not a guess


def test_turkey_has_seven_days():
    # Hapag-Lloyd Turkey tariff (effective 1 Jul 2026, all ports): import demurrage
    # combined with detention, 7 days for 20GP and 40GP/40HC.
    for text in ("Mersin, Turkey [TRMER]", "Mersin, Türkiye", "Ambarli, Turkiye"):
        assert days(text) == 7 and days(text, "DRY 40H") == 7
    c = HapagLloydAPIConnector()
    assert c._lookup_freetime("TRMER", "Mersin", "DRY 40") == (7, False)
