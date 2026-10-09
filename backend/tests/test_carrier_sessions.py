import pytest

from services import carrier_sessions as cs


STATE = {
    "cookies": [
        {"name": "auth", "value": "a", "domain": ".maersk.com", "path": "/", "expires": -1,
         "httpOnly": True, "secure": True, "sameSite": "Lax", "partitionKey": "x"},
        {"name": "sso", "value": "b", "domain": "accounts.maersk.com", "path": "/", "sameSite": "weird"},
        {"name": "other", "value": "c", "domain": ".google.com", "path": "/"},
        {"name": "fake", "value": "d", "domain": "notmaersk.com", "path": "/"},
    ],
    "origins": [
        {"origin": "https://www.maersk.com", "localStorage": [{"name": "token", "value": "t"}]},
        {"origin": "https://www.google.com", "localStorage": [{"name": "g", "value": "1"}]},
    ],
}


def test_clean_keeps_only_maersk_and_valid_fields():
    cleaned = cs.clean_storage_state("maersk", STATE)
    assert [c["name"] for c in cleaned["cookies"]] == ["auth", "sso"]
    assert "partitionKey" not in cleaned["cookies"][0]
    assert "sameSite" not in cleaned["cookies"][1]  # invalid value dropped
    assert cleaned["origins"] == [{"origin": "https://www.maersk.com", "localStorage": [{"name": "token", "value": "t"}]}]


@pytest.mark.parametrize("bad", [{}, {"cookies": "x"}, {"cookies": [{"name": "g", "value": "1", "domain": ".google.com"}]}])
def test_clean_rejects_files_without_maersk_cookies(bad):
    with pytest.raises(ValueError):
        cs.clean_storage_state("maersk", bad)


def test_unsupported_carrier():
    with pytest.raises(ValueError):
        cs.clean_storage_state("msc", STATE)


def test_save_load_delete_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    assert cs.session_info("maersk") is None
    info = cs.save_session("maersk", STATE, "brian")
    assert info["cookies"] == 2 and info["uploaded_by"] == "brian" and info["uploaded_at"]
    assert (tmp_path / "maersk_session.json").exists()
    assert cs.load_session("maersk")["cookies"][0]["name"] == "auth"
    assert cs.delete_session("maersk") is True
    assert cs.load_session("maersk") is None
