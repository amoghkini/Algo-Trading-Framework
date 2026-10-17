# Strategies

A strategy decides **what** to trade and **when to trigger** it. Everything else — placing orders, stop-loss,
target, trailing, square-off, persistence — is done by the [trading engine](trading-engine.md).

**Code:** `src/strategies/`, `src/restapis/strategies_api.py`, `src/templates/strategies.html`

## The strategy framework

Every strategy extends `BaseStrategy` and is a singleton obtained with `get_instance()`. The base class:

- registers the instance with `TradeManager` and reloads the strategy's trades from today's file after a restart;
- provides a fixed `run()` loop that must **not** be overridden;
- provides helpers for capital and lot sizing and for quotes.

### Configurable properties
| Property | Meaning |
|---|---|
| `name` | Unique strategy name (also the key in the `strategies` table and in trades) |
| `enabled` | Disabled strategies do not run |
| `product_type` | `MIS`, `NRML` or `CNC` |
| `symbols` | Symbols to scan (equity strategies) |
| `sl_percentage`, `target_percentage` | Stop-loss and target distances |
| `start_timestamp` | When the strategy starts scanning (default: market open 09:15) |
| `stop_timestamp` | After this time **no new trades** are triggered; existing ones stay active |
| `square_off_timestamp` | Time at which open trades are exited |
| `capital`, `leverage` | Money allocated to the strategy and multiplier |
| `max_trades_per_day` | Cap on triggered trades per day |
| `is_fno`, `capital_per_set` | F&O strategies: `lots = capital / capital_per_set` |

### `run()` loop (template method)
1. Exit if disabled, or the market is closed for the day / holiday.
2. If before 09:15, wait until market open.
3. Exit if `can_trade_today()` is false.
4. Sleep until `start_timestamp`.
5. Loop until market close: call `process()`, then sleep until the next :00 or :30 second mark.

### Hooks a strategy implements
| Hook | Purpose |
|---|---|
| `process()` | Look at quotes, build `Trade` objects, hand them to `TradeManager.add_new_trade()` (state `CREATED`) |
| `should_place_trade(trade, tick)` | Called on **every tick** for that symbol. Call `super()` first (it enforces qty > 0, the stop time and `max_trades_per_day`, disabling the trade otherwise), then add the entry condition |
| `can_trade_today()` | Optional day-of-week / expiry filter |
| `get_trailing_sl(trade)` | Optional trailing stop-loss; return `0` for "no change" |

### Writing a new strategy
1. Create `src/strategies/my_strategy.py` with a singleton subclass of `BaseStrategy`.
2. Set the properties in `__init__`, implement `process()` and `should_place_trade()`.
3. Add it to `Algo.start_algo()` so it gets a thread, and (for DB-driven parameters) insert a row in
   `algo_trader.strategies`.

## Bundled strategies

### `SAMPLE` — `SampleStrategy` (equity)
- Symbols: SBIN, INFY, TATASTEEL, RELIANCE, HDFCBANK, CIPLA.
- Parameters (times, capital, leverage, SL/target, max trades, product type) are **read from the
  `strategies` table** (`get_params()`), making it the example of a database-driven strategy.
- Logic: compute ±0.5 % around the previous close. **LONG** when the price is above the upper level,
  **SHORT** when below the lower level. Entry is triggered by the tick listener; SL/target use the configured
  percentages; quantity is `capital_per_trade / breakout_price` (minimum 1).

### `BNFORB30Min` — Bank Nifty opening-range breakout (futures)
- Instrument: monthly BANKNIFTY future. Window 09:45 → stop 14:30, square-off 15:00. Capital ₹1,00,000.
- Between 09:45 and 09:50 the day's high/low (≈ first 30 minutes) is read from the quote and two trades are
  created: **LONG at the high**, **SHORT at the low**.
- Stop-loss is the opposite end of the range; target is **1.5 × the range**.
- A trade triggers when the tick crosses its entry price.

### `OptionSelling` — Nifty weekly option selling
- Trades only on the **weekly expiry day or the day before** (`can_trade_today`).
- From 09:30, takes the Nifty monthly future price, finds the nearest 50-point ATM strike and **sells the
  ATM+50 CE and ATM−50 PE** (weekly options, `SHORT`).
- Stop-loss 50 % above the entry premium, no target. Stop 14:30, square-off 15:15. ₹1,00,000, one lot-set.

### `ShortStraddleBNF` — Bank Nifty short straddle
- From 11:00 sells the **ATM CE and ATM PE** (strike rounded to 100) of the weekly Bank Nifty options.
- Stop-loss 30 % above entry, no target. Stop 14:00, square-off 14:30.
- **Trailing SL:** for every 5 points of premium decay the stop-loss is lowered by 5 points
  (`get_trailing_sl`).

## Strategies page

`GET /strategies` (login required) lists the logged-in user's rows from `algo_trader.strategies`: name, start,
stop and square-off times, capital, F&O flag and capital per set. Rows are loaded into a pandas DataFrame and
rendered in `strategies.html`.

## Related tables
`algo_trader.strategies` — see [Database](database.md).
