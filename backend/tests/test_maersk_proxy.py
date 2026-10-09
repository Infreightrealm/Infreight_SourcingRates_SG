from carriers.maersk_connector import maersk_proxy_settings

VARS = ["MAERSK_PROXY_SERVER", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER",
        "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER", "BRIGHTDATA_RESIDENTIAL_PROXY_SERVER"]


def _clear(monkeypatch):
    for v in VARS:
        monkeypatch.delenv(v, raising=False)


def test_no_proxy_without_credentials(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MAERSK_PROXY_SERVER", "gw.dataimpulse.com:10000")
    assert maersk_proxy_settings() is None


def test_any_provider_uses_server_and_login_as_given(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MAERSK_PROXY_SERVER", "gw.dataimpulse.com:10000")
    monkeypatch.setenv("MAERSK_PROXY_USER", "abc123__cr.sg")
    monkeypatch.setenv("MAERSK_PROXY_PASS", "pw")
    assert maersk_proxy_settings() == {"server": "http://gw.dataimpulse.com:10000", "username": "abc123__cr.sg", "password": "pw"}


def test_bright_data_defaults_unchanged(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("BRIGHTDATA_PROXY_USER", "brd-customer-x-zone-res")
    monkeypatch.setenv("BRIGHTDATA_PROXY_PASS", "pw")
    monkeypatch.setenv("BRIGHTDATA_PROXY_SERVER", "http://brd.superproxy.io:33335")
    p = maersk_proxy_settings()
    assert p["server"] == "http://brd.superproxy.io:22225"
    assert p["username"].startswith("brd-customer-x-zone-res-session-")
