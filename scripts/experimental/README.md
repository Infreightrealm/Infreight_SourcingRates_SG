# CMA CGM SpotOn API experiment

Testing whether CMA CGM's **SpotOn pricing API** (`PRICING_API` v2.6.0) can
replace the Playwright connector.

**Nothing here is live.** The API connector is off unless `CMA_CGM_USE_API=true`,
and this work sits on the `claude/serene-noether-te6dct` branch, not `main` — so
Railway has not deployed it and the office laptop will not pick it up.

## Why it's worth trying

The browser connector exists mainly to look human to CMA CGM's bot defences. That
is the whole reason the office laptop runs crawls instead of the cloud. An
authenticated API call has no bot problem, so if this works, CMA CGM:

- returns in seconds rather than the 60–180s a browser crawl takes,
- can run on Railway permanently, unaffected by the laptop being off,
- stops breaking whenever CMA CGM redesign their website.

CMA CGM would become the first carrier that does not need the laptop at all.

## What the portal shows

Two separate things, and the difference matters:

| | Products | Can it price? |
|---|---|---|
| **Application 1** | `referential.*`, `vesseloperation.*`, `operation.trackandtrace.v1` | **No.** Locations, vessels, schedules, tracking only. |
| **SpotOn** | `GetSpotOn`, `CreateQuotationFromSpotOffer` | **Yes** — this is the one that matters. |

Two constraints come with it:

- **Security is OAuth2**, not a plain API-key header. Client credentials are
  exchanged for a bearer token; a bare key alone will not authenticate.
- **The quota is 20 requests/hour.** That is roughly six port pairs across three
  container sizes. Enough to prove the concept, nowhere near enough for a 168-pair
  batch — worth raising with CMA CGM before planning a rollout.

Only `GetSpotOn` is used here. `CreateQuotationFromSpotOffer` converts an offer
into a real quotation, which is a booking action, not a sourcing one.

## What is still needed

**The SpotOn Swagger.** Two things in the connector are educated guesses:

- `build_payload()` — the JSON body field names for `GetSpotOn`
- `FIELD_ALIASES` — the response field names

Export the Swagger from the SpotOn product page (the **Swagger** tab next to
Description and FAQ) and both become exact rather than guessed. Also needed from
it: the OAuth2 token URL, the scope, and the full path of `GetSpotOn`.

## Configuration

Everything goes in `.env` — no code change:

```
CMA_CGM_USE_API=true
CMA_CGM_API_BASE=https://apis.cma-cgm.net
CMA_CGM_API_TOKEN_URL=<from Swagger>
CMA_CGM_API_CLIENT_ID=<your client id>
CMA_CGM_API_CLIENT_SECRET=<your client secret>
CMA_CGM_API_SPOTON_PATH=<path of GetSpotOn>
```

## The probe script

`cma_api_probe.py` predates the SpotOn discovery — it was built to find out what a
plain API key could reach, and it answered that (referential/schedules only). It
is still useful for checking connectivity and which products respond, and it is
quota-aware: it stops at the first working auth header and spends at most
`--budget` requests, default 15 of the 20/hour.

```bash
python3 cma_api_probe.py --key YOUR_KEY --budget 8
```

It does **not** yet speak OAuth2, so it cannot exercise SpotOn itself. Once the
Swagger supplies the token URL, the connector is the thing to test, not the probe.

## What is already proven

Verified against a local fake gateway, since this sandbox is firewalled from CMA
CGM (`scripts/experimental/` tests plus `backend/tests/test_cma_api_connector.py`,
16 passing):

- the flag is off by default; the registry keeps returning the Playwright
  connector, and no other carrier is affected either way
- OAuth2 `client_credentials` exchange works, and the token is cached until
  expiry rather than re-minted per call — which matters at 20 requests/hour
- a 401 mid-batch re-mints the token and retries once before giving up
- three container types fetch and price independently over `POST GetSpotOn`
- BAF/LSS are included in the freight total and THC is excluded — the same
  classifier every other connector uses, so Excel export needs no changes
- a bad client secret reports a token rejection; a wrong path reports
  `CONNECTOR_NOT_AVAILABLE`; a 403 explains it may be a missing subscription —
  none is silently mistaken for "no rates"
- a nested charge list is never mistaken for the list of sailings (this was a real
  bug: three charges on one offer produced three phantom quotes)
- no credential is hardcoded in any file; the test suite asserts it

## Security

Credentials belong in `.env` or Railway environment variables, never in source.
A key or secret pasted into a chat should be rotated in the developer portal.
