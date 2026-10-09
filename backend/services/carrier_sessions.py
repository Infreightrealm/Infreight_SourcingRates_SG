"""Saved carrier logins uploaded by an admin.

An admin logs in to a carrier in real Chrome on their own PC
(scripts/export_maersk_login.py), which saves the logged-in cookies and
localStorage as a Playwright storage-state JSON. They upload it in Admin >
Carriers on / off, and the connector loads it into its browser so the server
starts signed in instead of logging in itself.

Stored on the persistent volume when there is one, like the carrier switches.
"""
import json
import os
import threading
from datetime import datetime
from typing import Optional

# Carrier -> cookie/origin domains its session lives on.
SESSION_DOMAINS = {"maersk": "maersk.com"}

_COOKIE_KEYS = ("name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite")
_lock = threading.Lock()


def _path(carrier: str) -> str:
    persistent = os.getenv("PERSISTENT_PROFILES_DIR")
    if persistent and os.path.isdir(persistent):
        return os.path.join(persistent, f"{carrier}_session.json")
    return os.path.join(os.path.dirname(__file__), "..", "data", f"{carrier}_session.json")


def _on_domain(host: str, domain: str) -> bool:
    host = host.lstrip(".").lower()
    return host == domain or host.endswith("." + domain)


def clean_storage_state(carrier: str, state: dict) -> dict:
    """Keep only this carrier's cookies and localStorage, in the shape add_cookies accepts.

    Raises ValueError when the file isn't a storage state or holds nothing for the carrier.
    """
    domain = SESSION_DOMAINS.get(carrier)
    if not domain:
        raise ValueError(f"Saved logins aren't supported for {carrier}")
    if not isinstance(state, dict) or not isinstance(state.get("cookies"), list):
        raise ValueError("This isn't a saved-login file (no cookies list).")

    cookies = []
    for c in state["cookies"]:
        if not isinstance(c, dict) or not c.get("name") or not _on_domain(str(c.get("domain", "")), domain):
            continue
        cookie = {k: c[k] for k in _COOKIE_KEYS if k in c}
        cookie.setdefault("path", "/")
        if cookie.get("sameSite") not in ("Strict", "Lax", "None"):
            cookie.pop("sameSite", None)
        cookies.append(cookie)

    origins = []
    for o in state.get("origins") or []:
        origin = str((o or {}).get("origin", ""))
        host = origin.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
        if not _on_domain(host, domain):
            continue
        items = [
            {"name": str(i["name"]), "value": str(i.get("value", ""))}
            for i in o.get("localStorage") or []
            if isinstance(i, dict) and "name" in i
        ]
        if items:
            origins.append({"origin": origin, "localStorage": items})

    if not cookies:
        raise ValueError(f"The file has no {domain} cookies. Log in to {domain} before exporting.")
    return {"cookies": cookies, "origins": origins}


def save_session(carrier: str, state: dict, actor: str) -> dict:
    cleaned = clean_storage_state(carrier, state)
    record = {
        **cleaned,
        "uploaded_by": actor,
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
    }
    path = _path(carrier)
    with _lock:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(record, f)
        os.replace(tmp, path)
    return session_info(carrier)


def load_session(carrier: str) -> Optional[dict]:
    try:
        with open(_path(carrier), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) and data.get("cookies") else None
    except (OSError, ValueError):
        return None


def session_info(carrier: str) -> Optional[dict]:
    """What the admin screen shows: who uploaded it, when, and how much it holds."""
    data = load_session(carrier)
    if not data:
        return None
    return {
        "uploaded_by": data.get("uploaded_by"),
        "uploaded_at": data.get("uploaded_at"),
        "cookies": len(data.get("cookies", [])),
    }


def delete_session(carrier: str) -> bool:
    try:
        os.remove(_path(carrier))
        return True
    except OSError:
        return False
