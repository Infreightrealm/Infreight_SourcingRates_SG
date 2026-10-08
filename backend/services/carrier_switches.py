"""Admin on/off switch per carrier, for when a carrier's site is down or under
maintenance. A switched-off carrier is skipped by searches (no browser opens)
and shown as off in the search form.

Kept on the persistent volume when there is one (Railway rebuilds /app on
every deploy), like the admin-saved port name fixes.
"""
import json
import os
import threading
from datetime import datetime
from typing import Optional

# The carriers people pick in the search form; HAPAG_LLOYD covers both its API and portal.
SWITCHABLE_CARRIERS = ["MAERSK", "CMA_CGM", "ONE", "HAPAG_LLOYD", "MSC", "GREENX", "OOCL"]

_lock = threading.Lock()


def _path() -> str:
    persistent = os.getenv("PERSISTENT_PROFILES_DIR")
    if persistent and os.path.isdir(persistent):
        return os.path.join(persistent, "carrier_switches.json")
    return os.path.join(os.path.dirname(__file__), "..", "data", "carrier_switches.json")


def _read() -> dict:
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def get_switches() -> dict:
    """Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on unless switched off."""
    saved = _read()
    return {
        code: {
            "enabled": bool(saved.get(code, {}).get("enabled", True)),
            "reason": saved.get(code, {}).get("reason"),
            "updated_by": saved.get(code, {}).get("updated_by"),
            "updated_at": saved.get(code, {}).get("updated_at"),
        }
        for code in SWITCHABLE_CARRIERS
    }


def set_switch(code: str, enabled: bool, reason: Optional[str], actor: str) -> dict:
    code = code.upper()
    if code not in SWITCHABLE_CARRIERS:
        raise ValueError(f"Unknown carrier {code}")
    with _lock:
        data = _read()
        data[code] = {
            "enabled": enabled,
            "reason": (reason or "").strip() or None if not enabled else None,
            "updated_by": actor,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        path = _path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    return get_switches()[code]


def off_message(code: str) -> Optional[str]:
    """The message for a switched-off carrier's result, or None when it is on."""
    code = (code or "").upper()
    if code == "HAPAG_LLOYD_API":
        code = "HAPAG_LLOYD"
    entry = get_switches().get(code)
    if not entry or entry["enabled"]:
        return None
    return f"Switched off by admin: {entry['reason']}" if entry["reason"] else "Switched off by admin (site down or under maintenance)"
