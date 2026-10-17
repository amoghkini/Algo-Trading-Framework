# Broker management

Users register their broker accounts, log in to them, and view live account data (orders, positions, holdings).
Only **Zerodha (Kite)** is implemented today; the code is structured so that another broker can be added by
providing new subclasses (see [Extending](#adding-another-broker)).

**Code:** `src/broker/`, `src/core/controller.py`, `src/login_management_system/`,
`src/broker_web_extenstions/kiteext.py`, `src/broker_transaction_management_system/`,
`src/restapis/{add_broker,my_brokers,login_broker,logout_broker,enquire_broker,orders,positions,holdings}_api.py`

## Features

### Add a broker
- Form (`BrokerCreateForm`): broker (currently `Zerodha`), broker/client id, password, app key, app secret key,
  32-character TOTP secret, auto-login (Yes/No).
- Stored in `algo_trader.brokers` against the logged-in user; `broker_id` is unique across the system, so adding
  the same account twice is rejected with a "already registered" message.
- New brokers start with status `Created` and login status `Yet to login`.

### My brokers page
Lists the user's brokers with broker id, name, status, login status and auto-login flag, with actions to log in
or out.

### Broker login
Three login methods are modelled in `BrokerLoginMethods`:

| Method | Constant | How it works | Implementation |
|---|---|---|---|
| Official API via broker portal | `api_with_broker_portal` | Redirects to Kite's login page; Kite redirects back with a `request_token` which is exchanged for an `access_token` using the app key/secret | `ZerodhaLogin` (`KiteConnect`) |
| Credentials, no token | `creds_without_enc_token` | Posts user id + password to Kite's web login, then answers 2FA with a **TOTP generated from the stored secret** (`pyotp`); reads the `enctoken` cookie | `ZerodhaWebLogin` + `KiteExt` |
| Credentials with enc token | `creds_with_enc_token` | User pastes an existing `enctoken`; it is used as the session | `ZerodhaWebLogin` + `KiteExt` |

Common behaviour (in `Controller.handle_broker_login`):
1. Read today's access token for this broker from `access_tokens`.
2. If one exists, **test it** by calling the broker profile API; if it is still valid, no new login happens
   (this avoids repeated logins and rate limits).
3. Otherwise run the login flow, then **upsert** the new token into `access_tokens` keyed by
   `(broker_id, token_date)` so a token is reused for the rest of the day.
4. Mark the broker `Logged in` in the `brokers` table.

The active login object is kept in `Controller.broker_login` (class-level state), and is what the order manager,
ticker, instruments loader and quote service use. Only **one broker session is active at a time**.

`KiteExt` details: subclass of `KiteConnect` that sends the Kite web front-end headers and an
`Authorization: enctoken …` header, overrides `_request` to use a `requests.Session`, and can build a
`KiteTicker` against `wss://ws.zerodha.com` using the enctoken.

### Broker logout
`/broker/logout?brokerID=<id>` sets the broker's login status to `Logged out`. On every application start-up all
brokers still marked `Logged in` are reset to `Logged out` (`BrokerMethods.logout_all_brokers`) so the database
never claims a session that no longer exists.

### Broker enquiry
`/broker/enquire/<broker_id>` renders a broker detail page (currently a placeholder with a header).

### Orders, positions and holdings
Read-only views of the live broker account, fetched through `ZerodhaTransactionManager`:

| Route | Returns |
|---|---|
| `/oms/orders` | JSON `{status, data}` with the day's order book |
| `/oms/positions` | JSON with current positions |
| `/oms/holdings` | JSON with delivery holdings |
| `/api/orders`, `/api/positions`, `/api/holdings` | HTML pages (`RedirectHandlerAPI`) that present the data |

`ZerodhaTransactionManager.test_connection()` calls `profile()` and is the "is my token still good?" probe.

## Endpoints

| Route | Methods | Purpose |
|---|---|---|
| `/broker/add` | GET, POST | Register a broker |
| `/brokers` | GET | List my brokers |
| `/broker/login` | GET, POST | Login form / login execution / API redirect target |
| `/broker/logout` | GET | Logout a broker |
| `/broker/enquire/<broker_id>` | GET | Broker detail page |
| `/oms/orders`, `/oms/positions`, `/oms/holdings` | GET | Account data (JSON) |

## Adding another broker
1. Add the name to `broker/brokers.py` and the broker form choices.
2. Subclass `BaseLogin`, `BaseOrderManager`, `BaseTicker`, `BaseTransactionManager`.
3. Wire the new classes into the `if broker_name == …` selectors in `Controller.handle_broker_login`,
   `BrokerMethods.get_transaction_manager`, `TradeManager.run` / `get_order_manager`, and `Quotes.get_quote`
   (the Fyers branches are already stubbed out as comments).

## Related tables
`algo_trader.brokers`, `algo_trader.access_tokens` — see [Database](database.md).
