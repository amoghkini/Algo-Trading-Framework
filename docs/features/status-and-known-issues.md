# Status, limitations and known issues

Honest notes on what is and is not finished, collected while documenting the code at git `HEAD`. Items are
grouped so they can be turned into tickets. See also `docs/to do` for the author's own backlog.

## Feature status

| Area | Status |
|---|---|
| Zerodha login (API portal, credentials + TOTP, enctoken) | Implemented |
| Other brokers (e.g. Fyers) | Not implemented — placeholders in comments only |
| Strategies, trade manager, order management, ticker | Implemented for Zerodha |
| Auto-login of brokers (`auto_login` flag) | Stored, not acted upon |
| Auto start / stop of the algo (SOD / EOD process) | Constants exist; process not built |
| Broker logout at the broker | Only the DB status changes; `ZerodhaLogin.logout()` is a stub |
| Telegram notifications | Sender implemented, not called anywhere yet |
| MongoDB | Wrapper exists; request hook disabled |
| Strategy parameters from DB | Only `SAMPLE`; the other strategies hard-code their parameters |
| Multi-user / multi-broker | Single active broker session (`Controller` static state); one algo for the whole app |
| CI | Lint and unit-test steps are placeholders; `tests/Test.py` is not a test suite |

## Bugs worth fixing first

These come from reading the code and have not been reproduced by running it.

1. **`TimeUtils.get_epoch()` and `get_time_of_day()` have an inverted condition**
   (`if datetime_obj: datetime_obj = datetime.now()`). A supplied datetime is ignored and replaced by *now*, and
   calling them with no argument fails (`None` has no `timestamp()` / `replace()`). Almost every strategy and
   trade timestamp goes through these helpers. The intended condition is `if not datetime_obj:`.
   (`src/utils/time_utils.py`)
2. **`SampleStrategy` reads the wrong column for stop-loss:** `self.sl_percentage = params.get('start_timestamp')`
   — the table column is `stop_loss_percentage`. (`src/strategies/sample_strategy.py`)
3. **`TradeManager.set_trade_to_completed` sets `trade.tradeState`** (camel-case typo) instead of
   `trade.trade_state`, so finished trades never leave the `active` state. (`src/trading_engine/trade_manager.py`)
4. **`ZerodhaOrderManager` compares with `OrderStatus.COMPLETED`**, but the enum member is `COMPLETE`.
   (`src/order_management_system/zerodha_order_manager.py`)
5. **`requirements.txt` is missing packages that the code imports:** `pika` (messaging), `pandas`
   (strategies page) and `pymongo` (Mongo wrapper). A clean install fails at import time.
6. **`Algo.stop_algo()` only closes the ticker.** The `TradeManager` loop and the strategy threads keep running
   until market close, and the "already stopped" branch does not return.
7. **`BrokerMethods.logout_broker`:** when no row was updated, `BrokerNotFoundError(...)` is created but never
   raised. (`src/broker/broker_methods.py`)
8. **Logout redirects to `/brokers`** rather than the login page. (`src/restapis/logout_api.py`)

## Security considerations

- `/algo/start`, `/algo/stop`, `/algo/status` and `/oms/*` **do not check that the caller is logged in**;
  `/algo/start` and `/algo/stop` are plain `GET` requests (state-changing, no CSRF protection).
- Broker passwords are stored **unencrypted** in `brokers.password`; TOTP secrets and API secrets are also stored
  in clear text.
- E-mail / password-reset tokens are signed with the literal default `'secret_key'`, and the Flask
  `SECRET_KEY` falls back to a placeholder. Set a real, secret value for both.
- The container runs `app.run(debug=True)` (Werkzeug dev server with the debugger enabled). Use a production WSGI
  server such as gunicorn (already in `requirements.txt`) and disable debug for any internet-facing deployment.
- Password hashes use `sha256_crypt`; `bcrypt`/`Flask-Bcrypt` are installed and would be a stronger choice.
- `KiteExt` fetches a User-Agent list from a third-party GitHub Pages URL at construction time.

## Robustness gaps

- `PostgresSql.query()` does not reconnect or retry; a dropped connection surfaces as an error.
- Trades are persisted to a JSON file rather than a database, so there is no history across days beyond the
  per-day folders.
- `TradeManager.get_last_traded_price` and `track_entry_order` index `symbol_to_cmp_map` directly and raise
  `KeyError` if no tick has arrived yet for a symbol.
- Instrument download failure on first run terminates the process (`exit(-2)`).
- The RabbitMQ host is hard-coded to `localhost`.
- Naming is partly camelCase in `BaseTicker` (`onConnect`, …); the backlog plans a snake_case migration.
- `docs/to do` also lists: moving broker login data fully to the DB, ajax start/stop, pandas-based processing,
  shared-memory order book for a future risk manager, and async requests.
