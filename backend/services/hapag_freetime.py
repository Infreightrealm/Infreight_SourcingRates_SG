"""Destination free time from config/hapag_freetime.json, shared by the Hapag-Lloyd
API and portal connectors."""
import re
from typing import Any, Mapping, Optional


def match_freetime_entry(config: Mapping[str, Any], text: str) -> Optional[tuple[str, Any]]:
    """The table entry whose country name appears in `text` as whole words.

    Whole words, so "Niger" doesn't match "Nigeria"; longest name first, so
    "Russia (Black Sea)" wins over a shorter overlapping name.
    """
    hay = f" {text.lower()} "
    for key in sorted(config, key=len, reverse=True):
        pattern = r"(?<![a-z])" + re.escape(key.lower()) + r"(?![a-z])"
        if re.search(pattern, hay):
            return key, config[key]
    return None


def freetime_days(entry: Any, container_type: str) -> Optional[int]:
    """Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare number)."""
    if isinstance(entry, dict):
        return entry.get("20GP" if "20" in (container_type or "") else "40GP", entry.get("40GP"))
    if isinstance(entry, int):
        return entry
    return None
