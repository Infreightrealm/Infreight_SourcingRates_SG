"""
Cleanup for Chrome browsers and temporary profiles that a failed close leaves behind.

A frozen Chrome ignores Playwright's close calls; their timeouts expire and the
connector moves on, leaving the browser and its helper processes running. Enough
of them exhaust the container's process/thread limit ("[Errno 11] Resource
temporarily unavailable"), and new browsers then show blank pages or "Aw, Snap".

Everything here reads /proc, so it only acts on Linux (production); elsewhere it
is a no-op. Master profiles (chrome_profile_<carrier>) are never deleted: only
per-search copies whose names contain "_tmp_".
"""
import os
import shutil
import signal
import time
import uuid
from typing import Iterable, Optional

PROFILE_CACHE_DIRS = ("Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache")
_CHROME_LOCK_FILES = ("SingletonLock", "lock", "SingletonCookie")
_STAGING_MARK = ".staging-"
_PREVIOUS_MARK = ".previous-"


def _proc_supported() -> bool:
    return os.name != "nt" and os.path.isdir("/proc")


def _read_processes() -> dict[int, tuple[int, list[str]]]:
    """pid -> (ppid, argv) for every readable process."""
    procs: dict[int, tuple[int, list[str]]] = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f"/proc/{pid}/stat", "rb") as f:
                stat = f.read().decode(errors="replace")
            # "pid (comm) state ppid ...": comm may contain spaces or ")".
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                argv = [a.decode(errors="replace") for a in f.read().split(b"\0") if a]
        except (OSError, ValueError, IndexError):
            continue
        procs[pid] = (ppid, argv)
    return procs


def _is_chrome(argv: list[str]) -> bool:
    if not argv:
        return False
    exe = os.path.basename(argv[0]).lower()
    return "chrome" in exe or "chromium" in exe or "headless_shell" in exe


def _is_playwright_driver(argv: list[str]) -> bool:
    return any(a == "run-driver" for a in argv) and any("playwright" in a or "patchright" in a for a in argv)


def _user_data_dir(argv: list[str]) -> Optional[str]:
    for a in argv:
        if a.startswith("--user-data-dir="):
            return os.path.realpath(a.split("=", 1)[1])
    return None


def _with_descendants(roots: Iterable[int], procs: dict[int, tuple[int, list[str]]]) -> set[int]:
    children: dict[int, list[int]] = {}
    for pid, (ppid, _) in procs.items():
        children.setdefault(ppid, []).append(pid)
    found: set[int] = set()
    stack = list(roots)
    while stack:
        pid = stack.pop()
        if pid in found:
            continue
        found.add(pid)
        stack.extend(children.get(pid, []))
    return found


def _kill(pids: set[int]) -> int:
    me = os.getpid()
    killed = 0
    for pid in pids:
        if pid in (me, 1):
            continue
        try:
            os.kill(pid, signal.SIGKILL)
            killed += 1
        except (ProcessLookupError, PermissionError):
            pass
    return killed


def kill_profile_browsers(profile_dir: Optional[str]) -> int:
    """
    Kill any Chrome still running on `profile_dir` (and its helper processes).
    Called after a connector's normal close, so a healthy close finds nothing.
    """
    if not profile_dir or not _proc_supported():
        return 0
    target = os.path.realpath(profile_dir)
    procs = _read_processes()
    roots = {pid for pid, (_, argv) in procs.items() if _is_chrome(argv) and _user_data_dir(argv) == target}
    if not roots:
        return 0
    killed = _kill(_with_descendants(roots, procs))
    if killed:
        print(f"[CLEANUP] Killed {killed} leftover Chrome process(es) for {os.path.basename(target)}")
    return killed


def sweep_orphan_browsers() -> int:
    """
    Kill every automated Chrome and Playwright driver. Only call this when no search
    or batch is running: it does not tell a live browser from a leftover one.
    """
    if not _proc_supported():
        return 0
    procs = _read_processes()
    me = os.getpid()
    roots = set()
    for pid, (ppid, argv) in procs.items():
        if _is_playwright_driver(argv):
            roots.add(pid)
        elif _is_chrome(argv) and (
            "--remote-debugging-pipe" in argv          # a Playwright-launched browser
            or ppid in (1, me)                          # orphaned helper of a dead browser
            or "_tmp_" in (_user_data_dir(argv) or "")  # a per-search profile copy
        ):
            roots.add(pid)
    if not roots:
        return 0
    killed = _kill(_with_descendants(roots, procs))
    if killed:
        print(f"[CLEANUP] Killed {killed} leftover browser process(es) while idle")
    return killed


def profile_base_dirs() -> list[str]:
    """Where connectors keep chrome_profile_* folders (see each connector's _init_browser)."""
    dirs = []
    persistent = os.getenv("PERSISTENT_PROFILES_DIR")
    if persistent:
        dirs.append(persistent)
    dirs.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
    return [d for d in dict.fromkeys(dirs) if os.path.isdir(d)]


def remove_stale_temp_profiles(keep: Iterable[str] = (), min_age_sec: float = 0) -> int:
    """
    Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and
    half-finished master swaps that no running search uses. Masters are untouched.
    A master whose swap was interrupted is restored from its previous copy first.
    """
    keep_real = {os.path.realpath(k) for k in keep if k}
    removed = 0
    now = time.time()
    for base in profile_base_dirs():
        try:
            entries = os.listdir(base)
        except OSError:
            continue
        for name in entries:
            path = os.path.join(base, name)
            if not name.startswith("chrome_profile") or not os.path.isdir(path):
                continue
            if _PREVIOUS_MARK in name:
                master = os.path.join(base, name.split(_PREVIOUS_MARK, 1)[0])
                if not os.path.exists(master):
                    try:
                        os.rename(path, master)
                        print(f"[CLEANUP] Restored master profile {os.path.basename(master)} from an interrupted save")
                    except OSError:
                        pass
                    continue
            elif "_tmp_" not in name and _STAGING_MARK not in name:
                continue  # a master profile: never deleted
            if os.path.realpath(path) in keep_real:
                continue
            try:
                if min_age_sec and now - os.path.getmtime(path) < min_age_sec:
                    continue
            except OSError:
                continue
            shutil.rmtree(path, ignore_errors=True)
            if not os.path.exists(path):
                removed += 1
    if removed:
        print(f"[CLEANUP] Removed {removed} leftover temporary profile folder(s)")
    return removed


def replace_master_profile(source_dir: str, master_dir: str) -> None:
    """
    Replace `master_dir` with a copy of `source_dir` (caches and lock files left out)
    without ever leaving the carrier without a master: the copy is built beside the
    master and swapped in by renames. An interruption leaves either the old master
    or a ".previous-" copy that remove_stale_temp_profiles() restores.
    """
    tag = uuid.uuid4().hex[:8]
    staging = f"{master_dir}{_STAGING_MARK}{tag}"
    previous = f"{master_dir}{_PREVIOUS_MARK}{tag}"
    shutil.copytree(source_dir, staging, ignore=shutil.ignore_patterns(*PROFILE_CACHE_DIRS, *_CHROME_LOCK_FILES))
    try:
        if os.path.exists(master_dir):
            os.rename(master_dir, previous)
        os.rename(staging, master_dir)
    except OSError:
        if not os.path.exists(master_dir) and os.path.exists(previous):
            os.rename(previous, master_dir)
        shutil.rmtree(staging, ignore_errors=True)
        raise
    shutil.rmtree(previous, ignore_errors=True)


def purge_carrier_profile(carrier: str) -> list[str]:
    """
    Delete master and temporary profiles for a given carrier across all base directories
    (e.g. PERSISTENT_PROFILES_DIR and local backend/).
    """
    carrier_lower = carrier.lower().strip()
    target_prefix = f"chrome_profile_{carrier_lower}"
    purged = []
    for base in profile_base_dirs():
        if not os.path.isdir(base):
            continue
        try:
            for entry in os.listdir(base):
                if entry.startswith(target_prefix):
                    path = os.path.join(base, entry)
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                        purged.append(path)
        except Exception as e:
            print(f"[CLEANUP] Error purging profiles in {base}: {e}")
    if purged:
        print(f"[CLEANUP] Purged {len(purged)} profile folder(s) for {carrier}: {purged}")
    return purged
