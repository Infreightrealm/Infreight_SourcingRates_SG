"""Maersk's login page redirects to the Hub a few seconds after loading when the
saved session is still valid; login() must wait for that instead of typing into
a form that never appears."""
import asyncio

from carriers.maersk_connector import MaerskConnector, _is_logged_in_url


class _Locator:
    def __init__(self, page):
        self._page = page

    async def count(self):
        return 1 if self._page.form_visible else 0


class _Page:
    """Sits on /portaluser/login, then redirects after `redirect_after` URL reads."""

    def __init__(self, redirect_after=None, form_visible=False):
        self._reads = 0
        self.redirect_after = redirect_after
        self.form_visible = form_visible

    def on(self, *_):
        pass

    @property
    def url(self):
        self._reads += 1
        if self.redirect_after is not None and self._reads > self.redirect_after:
            return "https://www.maersk.com/hub/"
        return "https://www.maersk.com/portaluser/login"

    def locator(self, *_):
        return _Locator(self)

    async def goto(self, *_, **__):
        pass

    async def wait_for_timeout(self, *_):
        pass


def _connector(page):
    c = MaerskConnector()
    c.page = page

    async def _no_browser():
        pass

    c._init_browser = _no_browser
    return c


def test_logged_in_url():
    assert _is_logged_in_url("https://www.maersk.com/hub/")
    assert not _is_logged_in_url("https://www.maersk.com/portaluser/login")
    assert not _is_logged_in_url("https://accounts.maersk.com/auth?redirect=/hub")


def test_wait_detects_late_redirect():
    c = _connector(_Page(redirect_after=4))
    assert asyncio.run(c._wait_for_session_or_login_form(timeout_sec=10)) == "session"


def test_wait_detects_login_form():
    c = _connector(_Page(form_visible=True))
    assert asyncio.run(c._wait_for_session_or_login_form(timeout_sec=10)) == "form"


def test_login_uses_saved_session_after_late_redirect(monkeypatch):
    monkeypatch.setenv("MAERSK_USERNAME", "user")
    monkeypatch.setenv("MAERSK_PASSWORD", "pass")
    c = _connector(_Page(redirect_after=4))
    assert asyncio.run(asyncio.wait_for(c.login(), timeout=10)) is True
    assert c.is_login_successful
