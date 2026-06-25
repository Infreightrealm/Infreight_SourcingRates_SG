# Performance Analysis — Infreight Sourcing Rates

**Goal:** make the multi-carrier scraping pipeline faster *without* weakening the
anti-bot safeguards that keep the carrier portals from blocking us.

**Scope of this document:** analysis and recommendations only. No code has been
changed. Findings are ordered by **impact ÷ risk** so the team can pick a starting
point.

---

## 1. The anti-bot layer — do NOT touch

These are the things that make the automation look human and keep IPs/sessions
un-banned. Every recommendation below is designed to leave them intact.

| Safeguard | Where | Why it stays |
|-----------|-------|--------------|
| Randomized human jitter (`wait_for_timeout(random.randint(...))`) | `maersk_connector.py:582-620`, and throughout | The variable cadence between keystrokes/clicks is exactly what fingerprinting looks for. Removing it is the #1 way to get banned. |
| Patchright stealth engine + `--disable-blink-features=AutomationControlled` | `maersk_connector.py:510`, `:549` | Defeats Akamai/Cloudflare automation detection. |
| Bright Data residential proxy w/ sticky session pinning | `maersk_connector.py:526-542` | Residential IP + stable session = looks like one returning user. |
| Persistent Chrome profiles & cookie-session reuse | `maersk_connector.py:670-697` | Avoids fresh-login fingerprints; lets us skip login entirely when a session is still valid. |
| `CARRIER_MAX_CONCURRENCY` cap | `job_service.py:274` | Caps simultaneous requests per IP. Keep the cap; it is already env-tunable. |
| CAPTCHA / 2FA human-in-the-loop (noVNC) | `base_connector.py:100` | Manual resolution path — unavoidable and correct. |

**The key insight:** the *random* delays are the safeguard. The *fixed* delays
are not — they are mostly "wait N seconds and hope the page finished loading."
Almost all of the speed-up below comes from fixing the fixed delays and the
I/O around them, never the random ones.

---

## 2. Where the time actually goes

There are **176** `sleep` / `wait_for_timeout` calls across the backend:

| Connector | Total wait calls | Notable fixed (blind) waits |
|-----------|------------------|------------------------------|
| `maersk_connector.py` | 60 | **10s** `:404`, **5s** `:667` & `:1995`, 3.5s `:635`, 3s `:916` & `:1971`, many 1–2s |
| `one_connector.py` | 33 | 2.5s `:456`, 3s `:883` & `:1022`, 2s `:982`, ~10× 1–1.5s |
| `cma_connector.py` | 20 | **4s** `:1062`, 2s `:719`/`:756`/`:770`, 1.5s `:841`/`:1055` |
| `greenx_connector.py` | 13 | 2s `:125`/`:432`, 1.5s `:262`, several 1s |
| `msc_connector.py` | 13 | 3s `:135`, 2s `:187`/`:321`/`:373` |
| `oocl_connector.py` | 9 | 3s `:228`/`:401`, several 1s |
| `hapag_lloyd_connector.py` | 8 | mostly `asyncio.sleep(1)`, one `sleep(2)` `:1832` |

Beyond the per-page waits, three structural costs dominate:

1. **Global single-search lock** — only one search runs system-wide at a time.
2. **Container types run sequentially** — a 2-type search does the full
   login→search→extract cycle twice, back to back.
3. **`slow_mo` on every action** — 80–150ms added to *every* Playwright call.

---

## 3. Recommendations

### Tier 1 — Safe wins, zero anti-bot impact

#### 1.1 Replace blind fixed waits with condition-waits
**Impact: high. Risk: low.**

The pattern to fix looks like this (Maersk login, runs on *every* search even
when the session is already restored):

```python
await self.page.goto("https://www.maersk.com/login", wait_until="load", timeout=60000)
await self.page.wait_for_timeout(5000)   # <-- always burns 5s
```

It should wait for the thing it actually needs, with the old value kept only as
a ceiling:

```python
await self.page.goto("https://www.maersk.com/login", wait_until="load", timeout=60000)
# Return the instant the login form (or logged-in marker) is present; 5s is now a cap, not a floor.
try:
    await self.page.wait_for_selector("mc-input, [class*='profile'], a[href*='logout']", timeout=5000)
except Exception:
    pass
```

This returns in ~200–800ms on a warm session instead of always 5s. Same idea for:

- `maersk_connector.py:404` — the **10s** wait after "Search more sailing
  options." Wait for the new quote cards to appear (`wait_for_selector` on the
  card container, or `wait_for_function` on card count increasing) instead.
- `maersk_connector.py:635`, `:1995`, `:916`, `:1971`
- `one_connector.py:456`, `:883`, `:982`, `:1022`
- `cma_connector.py:1062` (4s after "load more"), `:719`, `:756`, `:770`
- `msc_connector.py:135`, `:187`, `:321`, `:373`
- `oocl_connector.py:228`, `:401`
- `greenx_connector.py:125`, `:432`

**Rule of thumb for the conversion:**
- Wait *after a navigation* → `wait_for_load_state("domcontentloaded")` +
  `wait_for_selector(<the element you're about to use>)`.
- Wait *after a click that loads more data* →
  `wait_for_selector` / `wait_for_function` on the new content, or
  `expect(locator).to_be_visible()`.
- Keep the old number as the `timeout=` ceiling so the worst case never gets
  *slower*.
- **Leave every `random.randint(...)` wait exactly as-is.**

**Estimated saving: 15–40s per carrier on a warm-session run**, concentrated in
Maersk and ONE.

#### 1.2 Stop copying cache just to delete it
**Impact: medium (I/O, helps under concurrency). Risk: low.**

On close (`maersk_connector.py:2799-2829`), the flow is:
`rmtree(master)` → `copytree(temp → master)` of the **whole** profile (cache
included) → then walk `master` and delete the cache dirs.

Delete the cache dirs from `temp` **before** the copy, so the multi-hundred-MB
`Cache` / `Code Cache` / `GPUCache` / `DawnCache` / `ScriptCache` /
`CacheStorage` directories are never copied. Same end state, a fraction of the
bytes. (The same cache-dir list is already defined at `:2822` — reuse it.)

This repeats in `cma_connector.py` and `hapag_lloyd_connector.py`, which have the
same clone/sync structure (28 and 21 `copytree/rmtree/shutil` references
respectively).

#### 1.3 Cut queue-acquire latency
**Impact: low. Risk: low.**

`queue_manager.py:54` polls with `asyncio.sleep(2)`, adding up to 2s before a
search even starts. Drop to `0.5`. The `auto_release_poller` at
`job_service.py:329` sleeps 10s in a loop — fine to leave, or lower to 5s.

---

### Tier 2 — Bigger wins, small/medium risk

#### 2.1 Run container types concurrently
**Impact: high for multi-type searches. Risk: medium.**

`job_service.py:72` loops container types sequentially, each doing a full
`connector.run_full_search()` (login + search + extract). A 2-container-type
search therefore takes ~2× as long per carrier. Options, in order of preference:

- **Best:** reuse one logged-in browser session and re-run only the
  search→extract step per container type (avoids paying login N times). Requires
  a small connector refactor so the form can be re-submitted without re-launching.
- **Simpler:** run the container-type cycles concurrently under the existing
  semaphore budget. Easier, but multiplies live browser instances — watch RAM and
  the per-IP request rate (keep within `CARRIER_MAX_CONCURRENCY`).

#### 2.2 Trim `slow_mo`
**Impact: medium (compounds across hundreds of actions). Risk: low–medium.**

`maersk_connector.py:506` sets `slow_mo: random.randint(80, 150)`, applied to
*every* Playwright action. The genuine human cadence comes from the explicit
`random.randint` waits, not from `slow_mo`, so lowering this to ~`30–60ms` (or
making it env-tunable) shaves time off the entire run without flattening the
human-like jitter. Test one carrier first to confirm no new CAPTCHA pressure.

---

### Tier 3 — Largest win, architectural, needs a decision

#### 3.1 Relax the global single-search lock
**Impact: highest (throughput). Risk: high.**

`queue_manager.py` enforces **one search at a time across the entire system**,
even though each carrier already runs in an isolated temp profile on an isolated
display. With multiple users this is the hard ceiling — everyone queues.

The README's rationale ("single virtual display and browser context") is largely
already solved by the per-carrier profile/display isolation, so the lock may be
more conservative than necessary. Allowing e.g. 2 concurrent searches
(`Semaphore(2)` instead of a singleton lock) would roughly double throughput
under load. **Risk:** higher peak RAM/CPU and more simultaneous requests per
carrier IP — must be validated against both resource limits and anti-bot
thresholds before rollout. Recommend gating behind an env var and load-testing.

---

## 4. Suggested rollout order

1. **Tier 1.1 on Maersk only** — biggest, slowest connector; validates the
   condition-wait approach end-to-end against a real portal.
2. **Tier 1.2 + 1.3** — pure infra, no scraper-behavior change, low test burden.
3. **Tier 1.1 across the remaining connectors** (ONE → CMA → Hapag → GreenX →
   MSC → OOCL).
4. **Tier 2.2** (`slow_mo`) — one-line, easily reverted, measure CAPTCHA rate.
5. **Tier 2.1** (container-type concurrency) — needs a connector refactor + test.
6. **Tier 3.1** (global lock) — only after the above are proven, behind a flag,
   with load testing.

## 5. How to measure (so changes are provable, not vibes)

- Add coarse timing logs around each connector phase (login / search / extract /
  per-quote breakdown) and log the totals already printed at `job_service.py:201`.
- Compare warm-session vs cold-session runs — Tier 1.1's biggest gains only show
  on warm sessions (where the fixed waits were pure waste).
- Track CAPTCHA/2FA hit rate before and after Tier 2.2 / Tier 3.1 — that is the
  signal that an anti-bot threshold was crossed.
