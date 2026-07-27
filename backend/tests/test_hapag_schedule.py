import pytest
import re

def parse_hapag_card_text_mock(card_text: str):
    """Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py."""
    docCutoffMatch = re.search(r'Doc Cut-off\s+(\d{4}-\d{2}-\d{2})', card_text, re.IGNORECASE)
    fclCutoffMatch = re.search(r'FCL Cut-off\s+(\d{4}-\d{2}-\d{2})', card_text, re.IGNORECASE)
    vgmCutoffMatch = re.search(r'VGM Cut-off\s+(\d{4}-\d{2}-\d{2})', card_text, re.IGNORECASE)

    doc_cutoff = docCutoffMatch.group(1) if docCutoffMatch else ""
    fcl_cutoff = fclCutoffMatch.group(1) if fclCutoffMatch else ""
    vgm_cutoff = vgmCutoffMatch.group(1) if vgmCutoffMatch else ""

    cutoffDates = set(filter(None, [doc_cutoff, fcl_cutoff, vgm_cutoff]))

    allDates = re.findall(r'\d{4}-\d{2}-\d{2}', card_text)
    sailingDates = [d for d in allDates if d not in cutoffDates]
    activeDates = sailingDates if len(sailingDates) >= 2 else allDates

    if len(activeDates) < 2:
        return None

    etd = activeDates[0]
    eta = activeDates[-1]

    transit = None
    transitBadgeMatch = re.search(r'\b(\d+)\s*days?\b', card_text, re.IGNORECASE)
    if transitBadgeMatch:
        transit = int(transitBadgeMatch.group(1))

    return {
        "etd": etd,
        "eta": eta,
        "transit_time_days": transit,
        "sailing_dates": activeDates
    }


def test_hapag_multi_leg_schedule_extraction():
    """Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT."""
    mock_card_text = (
        "2026-08-09 2026-08-13 28 days 2026-09-06 "
        "Terminal / Ramp PASIR GUDANG, MYPGU "
        "PoL TANJUNG PELEPAS, MYTPP "
        "Terminal / Ramp (PoD) ALIAGA, TRALI "
        "Doc Cut-off 2026-08-10 "
        "FCL Cut-off 2026-08-10 "
        "VGM Cut-off 2026-08-10 "
        "SE3 MARIBO MAERSK Voyage no.: 631W"
    )

    res = parse_hapag_card_text_mock(mock_card_text)
    assert res is not None
    assert res["etd"] == "2026-08-09"
    assert res["eta"] == "2026-09-06"
    assert res["transit_time_days"] == 28
