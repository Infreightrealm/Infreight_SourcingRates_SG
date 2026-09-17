# CMA CGM SpotOn API experiment

Replacing the CMA CGM Playwright connector with the **SpotOn pricing API**
(`PRICING_API` v2.6.0, OpenAPI 3.0).

**Nothing here is live.** The API connector is off unless `CMA_CGM_USE_API=true`,
and this work sits on the `claude/serene-noether-te6dct` branch, not `main` — so
Railway has not deployed it and the office laptop will not pick it up.

## Do this first

```bash
python3 cma_spoton_test.py --client-id YOUR_ID --client-secret YOUR_SECRET
```

Runs anywhere with Python 3.8+ and internet. No pip install, no backend, no
Chrome, and it does not touch the repo. It gets a token, runs one real search
(Singapore → Hamburg, all three sizes), prints the offers and times it. **Costs 2
of your 20 hourly requests** and refuses to spend more than 4.

Change the route with `--pol SGSIN --pod DEHAM --sizes 20GP,40GP,40HC --date YYYY-MM-DD`.
The raw request and response land in `cma_spoton_out/`.

If it succeeds, send back `cma_spoton_out/response.json` — a real response lets
the connector's parser be checked against actual data rather than the spec's
examples.

## Then, to use it in the app

Only two values are needed; everything else defaults to the published spec.

```
CMA_CGM_USE_API=true
CMA_CGM_API_CLIENT_ID=<your client id>
CMA_CGM_API_CLIENT_SECRET=<your client secret>
```

## What the API gives us

| | Browser connector | SpotOn API |
|---|---|---|
| Time per search | 60–180s | seconds |
| Needs the office laptop | yes (bot defences) | **no** |
| Breaks when CMA redesign their site | yes | no |
| Requests per search | — | **1** for all three sizes |
| Sold-out detection | inferred from a blank cell | explicit `offerId` sentinel |
| Charge classification | our classifier guesses | carrier flags `includedInBasicFreight` |

CMA CGM would become the first carrier that does not need the laptop at all.

Three properties of the spec shaped the implementation:

- **`requestedEquipments` is an array.** 20', 40' and 40'HC are priced in one
  call, not three. At 20 requests/hour that difference matters.
- **Each charge carries `includedInBasicFreight`.** A charge already inside
  `basicOceanFreightRate` must not be added again or the total double-counts. The
  API also states its own `allInRate`, which we reconcile against ours — on a
  mismatch the carrier's figure wins and the quote carries a warning, rather than
  quietly publishing a number CMA would not honour.
- **Unavailability is explicit.** `offerId` carries `no-offer`, `Sold-out` or
  `Quantities cannot be confirmed`; `spotEquipments[].availableRate` reports it
  per size. No inferring emptiness from a blank cell — which is exactly the bug
  class that has plagued the scraping connectors.

## Limits worth knowing

- **20 requests/hour.** One search = one request, so ~20 port pairs an hour. Fine
  for proving this out; not enough for a 168-pair batch. Worth raising with CMA
  before planning a rollout.
- **Max 5 sailings per call** (`range` header, default `0-4`). More needs
  pagination, and each page is another request.
- **Departure date must be within today..today+30**, else `DAT_ERR`. The connector
  clamps rather than letting a search fail.
- **Local surcharges are not provided** — THC and documentation fees are absent by
  design, so an API quote's excluded charges are thinner than a scraped one's.
  That is the API's behaviour, not a parsing gap.
- **US/FMC routes are consultation only** and cannot be converted to a quotation.

## Files

| | |
|---|---|
| `cma_spoton_test.py` | Standalone live test. Start here. |
| `spoton-swagger-v2.6.0.json` | The API contract this was built against. |
| `cma_api_probe.py` | Earlier discovery tool, from before the spec was available. Still useful for checking which products a plain key reaches; it does not speak OAuth2, so it cannot exercise SpotOn. |
| `backend/carriers/cma_api_connector.py` | The connector. |
| `backend/tests/test_cma_api_connector.py` | 23 tests. |

## What is proven, and what is not

Verified (23 tests, fixtures built from the spec's own documented examples, plus
an end-to-end run against a local fake gateway — this sandbox is firewalled from
CMA CGM):

- the flag is off by default; the registry keeps returning the Playwright
  connector, and no other carrier is affected either way
- OAuth2 `client_credentials` works and the token is cached until expiry; a 401
  mid-batch re-mints once and retries
- all three sizes ride in one request, with every mandatory field present
- a charge flagged `includedInBasicFreight` is shown but never re-added
- a gap against `allInRate` is surfaced as a warning
- `Sold-out` / `no-offer` / `availableRate:false` never become priced quotes, and
  the reason is reported
- `Message` objects explaining an empty result are surfaced, not dropped
- ETD, ETA, transit, vessel, voyage, service, free days and validity all parse,
  and dates go through the shared normalizer so they match every other connector
- documented error codes map to distinct statuses — 400 bad input, 403 rights,
  416 range, 429 quota, 503 unavailable — none silently reads as "no rates"

**Not verified against the live API.** Every result above comes from the spec and
a fake gateway. Two things want a real response to confirm: the equipment ISO code
for 40' high cube (`40HC` is assumed — `referential.packaging.v2`, which your other
application has, lists the real codes), and whether `matchingBlSurcharges` carries
anything that should be excluded rather than included.

## Security

Credentials belong in `.env` or Railway environment variables, never in source.
The test suite asserts none is hardcoded. Anything pasted into a chat should be
rotated in the developer portal.
