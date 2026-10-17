# Utilities and market calendar

Shared helpers used by the engine and strategies.

**Code:** `src/utils/utils.py`, `src/utils/time_utils.py`, `src/utils/logger.py`, `src/common/`,
`src/exceptions/`

## Market calendar and timing (`Utils`)

| Helper | Description |
|---|---|
| `get_market_start_time()` / `get_market_end_time()` | 09:15 and 15:30 today (or on a given date) |
| `is_holiday(date)` / `is_today_holiday()` | Saturday/Sunday or a date listed in `config/holidays.json` |
| `is_market_open()` | Within market hours on a trading day |
| `is_market_closed_for_the_day()` | Holiday, or after 15:30 |
| `wait_till_market_opens(context)` | Sleeps until 09:15 and logs who is waiting |

## Derivatives helpers

| Helper | Description |
|---|---|
| `get_monthly_expiry_day_date()` | Last Thursday of the month, moved back past holidays |
| `get_weekly_expiry_day_date()` | Thursday of the current week, moved back past holidays |
| `is_today_weekly_expiry_day()`, `is_today_one_day_before_weekly_expiry_day()` | Used by `OptionSelling.can_trade_today()` |
| `prepare_monthly_expiry_futures_symbol('BANKNIFTY')` | e.g. `BANKNIFTY24MARFUT`; rolls to next month after expiry day opens |
| `prepare_weekly_options_symbol(name, strike, 'CE'/'PE', weeks_ahead)` | Builds the Kite weekly option symbol for the relevant expiry |
| `get_nearest_strike_price(price, multiple)` | Rounds to the nearest strike (50 for Nifty, 100 for Bank Nifty) |

## Pricing and P&L
- `round_to_nse_price(price)` — rounds **up** to the NSE tick size of ₹0.05.
- `round_off(price)` — 2 decimals.
- `calculate_trade_pnl(trade)` — realised/unrealised P&L and percentage (see [Trading engine](trading-engine.md#pnl)).
- `generate_trade_id()` — UUID4.

## Time helpers (`TimeUtils`)
Epoch conversion (`get_epoch`), building a datetime for a time of day or today (`get_time_of_day`,
`get_time_of_today`), and date/time ⇄ string conversion with the formats `%Y-%m-%d`, `%H:%M:%S` and
`%Y-%m-%d-%H-%M-%S`. Timestamps stored in the database and trade file are epoch seconds.

## Other helpers
- `get_external_url(endpoint, args)` — absolute URL for e-mailed links.
- `get_mismatches_from_two_dict()` — returns only the changed fields, used so profile updates write the minimum.
- `get_config()`, `get_execution_env()`, `get_log_dir()` — read `server.json`.
- `common/singleton.py` — `SingletonMeta` metaclass; `common/execution_env.py` — `dev`/`test`/`prod`;
  `common/redirect_page.py` — page names accepted by `/api/<page_name>`.

## Exceptions (`src/exceptions/`)
| Module | Types |
|---|---|
| `api_exceptions` | `APIException`, `DataException`, `DatabaseWriteError`, `DuplicateEntryError` |
| `broker_exceptions` | `BrokerAuthError`, `BrokerTOTPError`, `BrokerNotFoundError`, `BrokerError`, `InvalidUBrokerDataError` |
| `user_exceptions` | `AuthUserError`, `InvalidUserDataError`, `UserNotFoundError`, `UserSignatureError` |
| `strategy_exceptions` | `StrategyNotFoundError` |

REST views translate these into flash messages or JSON `fail` responses.
