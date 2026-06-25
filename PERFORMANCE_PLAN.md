# Performance Implementation Plan

Companion to `PERFORMANCE_ANALYSIS.md`. This is the **plan only** — no code is
changed yet. It covers the three scopes you approved and explicitly excludes the
one you rejected.

| # | Scope | Risk | Decision |
|---|-------|------|----------|
| 1 | Profile cache exclusion | None | ✅ implement |
| 2 | Queue/event responsiveness | None | ✅ implement |
| 3 | Smart waits (blind → conditional, via safe wrapper) | Medium | ✅ implement, Maersk first |
| 4 | Share session across container types | High | ❌ excluded (not recommended) |

---

## Scope 1 — Profile cache exclusion (zero risk)

**Idea:** never copy the throwaway browser caches when cloning the master profile
into a temp dir, nor when syncing back. Cookies / Local Storage / IndexedDB
(the session) live in their own files and are still copied, so login state is
fully preserved. Chromium recreates empty cache dirs on launch.

**Affected files (only these three clone profiles):**
`maersk_connector.py`, `cma_connector.py`, `hapag_lloyd_connector.py`.
`one/greenx/msc/oocl` do **not** clone profiles — no change there.

### 1a. Shared constant
Add once per connector module (or a shared `carriers/_profile_util.py`):

```python
# Throwaway dirs + Chromium lock files we never want copied.
_PROFILE_SKIP = (
    "Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage",
    "ScriptCache", "Service Worker", "GrShaderCache", "GraphiteDawnCache",
    "SingletonLock", "SingletonCookie", "lock",
)
```

### 1b. Clone (launch side)
**`maersk_connector.py:478`**, **`cma_connector.py:77`**, **`hapag_lloyd_connector.py:103`**

```python
# BEFORE
shutil.copytree(self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True)
# ...then a separate os.walk to delete SingletonLock/lock/SingletonCookie

# AFTER
shutil.copytree(
    self.master_profile_dir, self.temp_profile_dir,
    dirs_exist_ok=True,
    ignore=shutil.ignore_patterns(*_PROFILE_SKIP),
)
# lock-file removal walk becomes unnecessary (locks are now never copied) — delete it
```

### 1c. Sync back (close side)
**`maersk_connector.py:2808`**, **`cma_connector.py:1282`**, **`hapag_lloyd_connector.py:3073`**

```python
# BEFORE
shutil.copytree(self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True)
# ...then os.walk over master to rmtree cache_dirs (copies GBs, then deletes them)

# AFTER
shutil.copytree(
    self.temp_profile_dir, self.master_profile_dir,
    dirs_exist_ok=True,
    ignore=shutil.ignore_patterns(*_PROFILE_SKIP),
)
# the post-copy cache-deletion walks (maersk:2822-2829, cma:1294-1302, hapag:3076-3084)
# are now redundant — delete them
```

**Net effect:** the multi-hundred-MB `Cache`/`GPUCache`/etc. trees are never read
or written during clone **or** sync. Same session fidelity, a fraction of the
disk I/O — and the savings compound when carriers run concurrently.

**Verification:** after a search, confirm `chrome_profile_*` still contains
`Cookies`, `Local Storage`, `IndexedDB`; confirm the next search still reports
"Session restored / Already logged in" (`maersk:695`). No cache dirs should
appear in the master profile.

---

## Scope 2 — Queue/event responsiveness (zero risk)

**Idea:** replace the 2-second polling loop in the queue with an
`asyncio.Condition` so the next search starts the instant a slot frees up.

**File:** `services/queue_manager.py`

### 2a. Use a Condition bound to the existing lock
```python
def __init__(self):
    ...
    self._lock = asyncio.Lock()
    self._cond = asyncio.Condition(self._lock)   # NEW — shares the same lock
    ...
```

### 2b. `enqueue_and_wait` — wait instead of poll (replaces `:34-54`)
```python
async def enqueue_and_wait(self, search_id: str, search_info: str) -> None:
    async with self._cond:
        if search_id not in self.queue and self.active_search_id != search_id:
            self.queue.append(search_id)
            self.queue_info[search_id] = search_info
        while True:
            if search_id not in self.queue and self.active_search_id != search_id:
                raise asyncio.CancelledError("Search was cancelled or removed from queue.")
            if self.active_search_id is None and self.queue and self.queue[0] == search_id:
                self.active_search_id = self.queue.pop(0)
                self.active_search_info = self.queue_info.pop(search_id, "Unknown Route")
                return
            if self.active_search_id == search_id:
                return
            await self._cond.wait()        # releases lock, wakes on notify — no 2s poll
```

### 2c. Notify on every state change
In `release_lock` (`:82`), `auto_release_check` (`:108`), and `force_clear_all`
(`:129`): switch `async with self._lock:` → `async with self._cond:` and add
`self._cond.notify_all()` right after the lines that clear/alter
`active_search_id`/`queue`. That wakes all waiters; each re-checks whether it is
now first in line.

**Notes:**
- `_cond.wait()` atomically releases and re-acquires the lock; cancellation
  propagates cleanly (same `CancelledError` semantics as today).
- The `auto_release_poller` in `job_service.py:327-339` is a **timeout**, not a
  pollable event, so it stays — optionally drop its `sleep(10)` to `sleep(5)`.
  It no longer affects start latency.

**Verification:** queue two searches; the second should start within
milliseconds of the first releasing, not up to 2s later.

---

## Scope 3 — Smart waits via a safe wrapper (medium risk, Maersk first)

**Idea:** replace blind `wait_for_timeout(N)` "wait and hope" calls with a wait
that returns the instant the page is ready, keeping `N` only as a **ceiling**.
A safe wrapper guarantees we never crash where a blind sleep would have
survived: on timeout it logs and continues.

> **Untouched:** every `wait_for_timeout(random.randint(...))` jitter call stays
> exactly as-is. This scope only touches *fixed* waits that gate on page state.

### 3a. The wrapper (add to `base_connector.py`)
```python
async def wait_ready(self, selectors, timeout: int = 5000, label: str = "") -> bool:
    """
    Wait until any of `selectors` is visible, capped at `timeout` ms.
    Never raises — logs and returns False on timeout, matching the old blind-sleep
    behavior (continue anyway). Returns True if a selector appeared.
    """
    if not self.page:
        return False
    if isinstance(selectors, str):
        selectors = [selectors]
    async def _one(sel):
        await self.page.locator(sel).first.wait_for(state="visible", timeout=timeout)
        return sel
    tasks = [asyncio.ensure_future(_one(s)) for s in selectors]
    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
        for t in done:
            if not t.cancelled() and t.exception() is None:
                return True
        return False
    except Exception:
        return False
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()
        print(f"[{self.carrier_code}] wait_ready({label or selectors}) "
              f"settled (cap {timeout}ms)")
```

This handles `:has-text(...)` and CSS selectors alike (locator-based), and races
multiple candidate selectors — important because these portals expose several
possible markers.

### 3b. Rollout: Maersk first, then the rest
Validate the wrapper on Maersk (the slowest connector) before touching others.

**Top Maersk conversions (full before/after):**

`maersk_connector.py:667` — post-login hydration wait (runs even on warm sessions):
```python
# BEFORE
await self.page.wait_for_timeout(5000)
# AFTER — login form OR an already-logged-in marker; 5s is now a cap
await self.wait_ready(
    ['mc-input', 'mc-button', '[class*="profile"]', 'a[href*="logout"]'],
    timeout=5000, label="login-page-ready")
```

`maersk_connector.py:404` — after clicking "Search more sailing options":
```python
# BEFORE
await self.page.wait_for_timeout(10000)
# AFTER — wait for the new sailing cards to render (use the card selector from
# extract_quote_list; confirm exact selector during implementation)
await self.wait_ready([<sailing-card selector>], timeout=10000, label="more-sailings")
```

`maersk_connector.py:375` — settle after `scrollTo`, before locating the button:
the following block (`:390-397`) already probes the button with
`is_visible(timeout=1500)`, so this 2s pre-wait is largely redundant — reduce to
a short settle (e.g. 300ms) or fold into `wait_ready` on the button selectors at
`:377-387`.

### 3c. Conversion table (target condition confirmed per-site at implementation)
Each entry: replace the fixed wait with `wait_ready([...], timeout=<same value>)`
keyed to the element the code uses immediately after.

| File | Lines | Current | Target condition |
|------|-------|---------|------------------|
| maersk | 635, 916, 1971, 1995 | 3.5–5s | results/breakdown container visible |
| maersk | 883, 1364, 1625, 1912, 2465 | 2s | next clicked element / dialog visible |
| one | 456 | 2.5s | search form rendered |
| one | 883 | 3s | new calendar dates rendered |
| one | 982, 1022 | 2–3s | quote cards / detail panel visible |
| one | 494, 506, 521, 568, 580, 595 | 1.5s | dropdown option visible |
| one | 183, 360, 988, 1209 | 1s | post-action element visible |
| cma | 1062 | 4s | new quote cards loaded |
| cma | 719, 756, 770 | 2s | results / panel visible |
| cma | 841, 1055 | 1.5s | element visible |
| msc | 135, 187, 321, 373 | 2–3s | page/element visible |
| oocl | 228, 401 | 3s | expansion / dropdown rendered |
| greenx | 125, 432 | 2s | page JS / results visible |
| greenx | 262 | 1.5s | suggestions rendered |
| hapag | 1832 | 2s | element visible |

**Leave alone:** sub-500ms waits used as micro-settles after animations, and all
`random.randint` jitter. Converting those buys little and adds churn.

**Per-site rule:**
1. Identify the element the code touches *right after* the wait.
2. `wait_ready([that selector], timeout=<old value>)`.
3. If the page can be in multiple valid states, pass all candidate selectors.
4. Old value stays as the ceiling → worst case is never slower than today.

**Why this is safe despite "medium" risk:** the wrapper *never raises*. If a
carrier changes its HTML and a selector stops matching, we burn the full
ceiling (today's behavior) and continue — identical to the current blind sleep.
The downside of a stale selector is "no speed-up here," not "crash."

---

## Scope 4 — Share session across container types (EXCLUDED)

Not implementing. Reusing one logged-in browser across container types means
re-driving carrier SPA state machines (notably Hapag-Lloyd and ONE), which is
fragile and can trip anti-bot/state bugs. A fresh, clean session per cycle is
more stable. Revisit only if multi-container searches become a measured
bottleneck.

---

## Suggested order & validation

1. **Scope 1** (cache exclusion) — verify session still restores; check master
   profile has no cache dirs.
2. **Scope 2** (queue Condition) — verify 2nd queued search starts instantly.
3. **Scope 3 on Maersk** — time a warm-session run before/after; watch CAPTCHA
   rate.
4. **Scope 3 on ONE → CMA → Hapag → GreenX → MSC → OOCL** — one connector per
   commit so regressions are easy to bisect.

Each scope is independent and separately revertible.
