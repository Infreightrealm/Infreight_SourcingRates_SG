"""
Leftover browser and profile cleanup (services/browser_cleanup.py).

The profile tests run anywhere. The process tests launch a real Chromium and only
run when CLEANUP_TEST_CHROME points at a Chrome/Chromium binary on Linux.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import time

import pytest

from services import browser_cleanup as bc


@pytest.fixture
def profiles(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSISTENT_PROFILES_DIR", str(tmp_path))
    return tmp_path


def _make_profile(path, cookie="session-a"):
    (path / "Default").mkdir(parents=True)
    (path / "Default" / "Cookies").write_text(cookie)
    (path / "Default" / "Cache").mkdir()
    (path / "Default" / "Cache" / "blob").write_text("x" * 100)
    (path / "SingletonLock").write_text("")


def test_masters_are_never_deleted(profiles):
    for name in ("chrome_profile_maersk", "chrome_profile_one", "chrome_profile_hapag_EU"):
        _make_profile(profiles / name)
    for name in ("chrome_profile_maersk_tmp_aaaa1111", "chrome_profile_hapag_EU_tmp_bbbb2222"):
        _make_profile(profiles / name)

    assert bc.remove_stale_temp_profiles() == 2
    assert sorted(p.name for p in profiles.iterdir()) == [
        "chrome_profile_hapag_EU", "chrome_profile_maersk", "chrome_profile_one",
    ]


def test_profiles_in_use_or_too_new_are_kept(profiles):
    in_use = profiles / "chrome_profile_one_tmp_live0001"
    fresh = profiles / "chrome_profile_cma_tmp_new00002"
    old = profiles / "chrome_profile_cma_tmp_old00003"
    for p in (in_use, fresh, old):
        _make_profile(p)
    an_hour_ago = time.time() - 3600
    os.utime(in_use, (an_hour_ago, an_hour_ago))
    os.utime(old, (an_hour_ago, an_hour_ago))

    assert bc.remove_stale_temp_profiles(keep=[str(in_use)], min_age_sec=600) == 1
    assert in_use.exists() and fresh.exists() and not old.exists()


def test_replace_master_profile_swaps_in_a_clean_copy(profiles):
    master = profiles / "chrome_profile_maersk"
    temp = profiles / "chrome_profile_maersk_tmp_cccc3333"
    _make_profile(master, cookie="old-session")
    _make_profile(temp, cookie="new-session")

    bc.replace_master_profile(str(temp), str(master))

    assert (master / "Default" / "Cookies").read_text() == "new-session"
    assert not (master / "Default" / "Cache").exists()  # caches are not copied
    assert not (master / "SingletonLock").exists()       # nor Chrome lock files
    assert sorted(p.name for p in profiles.iterdir()) == ["chrome_profile_maersk", temp.name]


def test_an_interrupted_save_restores_the_master(profiles):
    # A crash between the two renames leaves only the ".previous-" copy.
    _make_profile(profiles / "chrome_profile_maersk.previous-dddd4444", cookie="good-session")
    _make_profile(profiles / "chrome_profile_maersk.staging-dddd4444", cookie="half-copied")

    bc.remove_stale_temp_profiles()

    assert (profiles / "chrome_profile_maersk" / "Default" / "Cookies").read_text() == "good-session"
    assert sorted(p.name for p in profiles.iterdir()) == ["chrome_profile_maersk"]


def test_purge_carrier_profile(profiles):
    _make_profile(profiles / "chrome_profile_maersk")
    _make_profile(profiles / "chrome_profile_maersk_tmp_1234")
    _make_profile(profiles / "chrome_profile_one")

    purged = bc.purge_carrier_profile("maersk")
    assert any("chrome_profile_maersk" in p for p in purged)
    assert not (profiles / "chrome_profile_maersk").exists()
    assert not (profiles / "chrome_profile_maersk_tmp_1234").exists()
    assert (profiles / "chrome_profile_one").exists()


CHROME = os.getenv("CLEANUP_TEST_CHROME")
needs_chrome = pytest.mark.skipif(
    not CHROME or os.name == "nt", reason="set CLEANUP_TEST_CHROME to a Chrome binary (Linux) to run"
)


def _chrome_pids(procs=None):
    procs = procs or bc._read_processes()
    return {pid for pid, (_, argv) in procs.items() if bc._is_chrome(argv)}


@needs_chrome
@pytest.mark.asyncio
async def test_kill_profile_browsers_kills_a_browser_that_was_never_closed(profiles):
    from playwright.async_api import async_playwright

    profile = profiles / "chrome_profile_one_tmp_eeee5555"
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(str(profile), executable_path=CHROME, args=["--no-sandbox"])
    page = await ctx.new_page()
    await page.goto("data:text/html,<h1>stuck</h1>")
    try:
        procs = bc._read_processes()
        mine = {pid for pid, (_, argv) in procs.items() if bc._user_data_dir(argv) == os.path.realpath(profile)}
        assert mine, "the test browser should be running on the profile"

        # Simulate a frozen browser: skip ctx.close() and go straight to the fallback.
        assert bc.kill_profile_browsers(str(profile)) >= len(mine)
        await asyncio.sleep(0.5)
        assert not (_chrome_pids() & mine)
    finally:
        await pw.stop()


@needs_chrome
@pytest.mark.asyncio
async def test_idle_sweep_kills_every_leftover_browser_and_driver():
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    await (await browser.new_page()).goto("data:text/html,<h1>leftover</h1>")
    try:
        assert _chrome_pids()
        assert bc.sweep_orphan_browsers() > 0
        await asyncio.sleep(0.5)
        assert not _chrome_pids()
        assert not any(bc._is_playwright_driver(argv) for _, argv in bc._read_processes().values())
    finally:
        try:
            await asyncio.wait_for(pw.stop(), timeout=3)
        except Exception:
            pass
