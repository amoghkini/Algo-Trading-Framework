# Market data

Live ticks, on-demand quotes and the instrument master.

**Code:** `src/ticker/`, `src/core/quotes.py`, `src/instruments/instruments.py`,
`src/models/{quote,tick_data}.py`

## Live ticker (streaming)

- `BaseTicker` — interface and **listener fan-out**: `register_listener(fn)`, `on_new_ticks(ticks)` which calls
  every listener (exceptions in one listener are logged, not propagated), plus connection-event hooks
  (`onConnect`, `onDisconnect`, `onError`, `onReconnect`, `onMaxReconnectsAttempt`, `onOrderUpdate`).
- `ZerodhaTicker` — wraps `KiteTicker`:
  - connects in a background thread with the day's access token;
  - `register_symbols()` / `unregister_symbols()` translate trading symbols to instrument tokens and
    subscribe/unsubscribe;
  - `on_ticks` converts the broker's tick dictionaries into the internal `TickData` model (last price/quantity,
    average price, volume, total buy/sell quantity, OHLC, change) before notifying listeners.
- `TradeManager` is the single listener; it subscribes symbols lazily when a trade is added or reloaded.

## Quotes (on demand)

`Quotes.get_quote(symbol, is_fno=False)` calls the broker quote API (`NSE:` or `NFO:` prefix) and maps the
response to the internal `Quote` model: last traded price/quantity, average price, volume, buy/sell quantity,
OHLC, net change, OI day high/low, lower/upper circuit limits. `Quotes.get_cmp(symbol)` returns just the last
traded price (0 when unavailable). Strategies use quotes in `process()` to decide what trades to create.

## Instrument master

`Instruments` loads and caches the tradeable universe (NSE equity + NFO derivatives):

1. `fetch_instruments()` returns the in-memory list if already loaded.
2. Otherwise reads `python-deploy/instruments.json`.
3. If the file is missing/empty, or it was saved **24 hours or more ago** (tracked in `timestamps.json` as
   `instrumentsLastSavedAt`), downloads both segments from the broker and rewrites the file.
4. If nothing can be loaded, the application logs an error and exits.
5. Builds two lookup maps: `trading symbol → instrument` and `instrument token → instrument`.

`get_instrument_data_by_symbol()` is used, for example, to find an option's **lot size** when sizing a trade,
and the ticker uses both maps to translate between symbols and tokens.

## Models

| Model | Used for |
|---|---|
| `Quote` | Result of a point-in-time quote request |
| `TickData` | One streamed tick |
