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
