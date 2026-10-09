"""Saving the Maersk session back to the master profile survives Chrome's file locks on Windows."""
import asyncio
import os

from carriers import maersk_connector
from carriers.maersk_connector import MaerskConnector
from services import browser_cleanup


def test_profile_save_retries_while_chrome_holds_files(tmp_path, monkeypatch):
    temp = tmp_path / "chrome_profile_maersk_tmp_x"
    (temp / "Default").mkdir(parents=True)
    (temp / "Default" / "Cookies").write_text("session")
    master = tmp_path / "chrome_profile_maersk"

    real = browser_cleanup.replace_master_profile
    calls = []

    def flaky(src, dst):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError("[WinError 32] The process cannot access the file because it is being used")
        real(src, dst)

    monkeypatch.setattr(browser_cleanup, "replace_master_profile", flaky)

    async def no_wait(_):
        return None

    monkeypatch.setattr(maersk_connector.asyncio, "sleep", no_wait)

    c = MaerskConnector()
    c.temp_profile_dir, c.master_profile_dir, c.is_login_successful = str(temp), str(master), True
    asyncio.run(c.close())

    assert len(calls) == 3
    assert (master / "Default" / "Cookies").read_text() == "session"
    assert not temp.exists()
    assert not [n for n in os.listdir(tmp_path) if ".staging-" in n]


def test_failed_copy_leaves_no_staging_folder(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a").write_text("x")

    made = []

    def boom(_src, dst, **_k):
        os.makedirs(dst)  # half-written copy, then a locked file
        made.append(dst)
        raise PermissionError("locked")

    monkeypatch.setattr(browser_cleanup.shutil, "copytree", boom)
    try:
        browser_cleanup.replace_master_profile(str(src), str(tmp_path / "chrome_profile_maersk"))
    except PermissionError:
        pass
    assert made and ".staging-" in made[0]
    assert not os.path.exists(made[0])
