# Trading engine

`TradeManager` is the heart of the framework. It receives trades from the strategies, triggers them on live
ticks, places the entry / stop-loss / target orders, keeps the trade state in sync with the broker, and saves
everything to disk.

**Code:** `src/trading_engine/` (`trade_manager.py`, `trade.py`, `trade_state.py`, `trade_exit_reason.py`,
`trade_encoder.py`)

## The `Trade` entity

One object per intended position. Key fields:

| Group | Fields |
|---|---|
| Identity | `trade_id` (UUID), `strategy`, `trading_symbol`, `exchange` |
| Instrument | `direction` (`LONG`/`SHORT`), `product_type`, `is_futures`, `is_options`, `option_type` |
| Entry | `place_market_order`, `requested_entry`, `entry` (actual average price), `qty`, `filled_qty` |
| Risk | `initial_stop_loss`, `stop_loss` (current, changes when trailing), `target` |
| Timing | `timestamp`, `create_timestamp`, `start_timestamp`, `end_timestamp`, `intraday_square_off_timestamp` |
| Result | `cmp`, `pnl`, `pnl_percentage`, `exit`, `exit_reason` |
| Orders | `entry_order`, `sl_order`, `target_order` (`Order` objects) |

Two trades are considered equal if they have the same id, or the same symbol/strategy/direction/product/entry/
qty/timestamp — this prevents a strategy that re-runs `process()` every 30 s from adding duplicates.

### States (`TradeState`)
`created` → `active` → `completed`; or `cancelled` / `disabled`. See the state diagram in
[architecture](../architecture.md#5-trade-lifecycle).

### Exit reasons (`TradeExitReason`)
`SL HIT`, `TRAIL SL HIT`, `TARGET HIT`, `SQUARE OFF`, `SL CANCELLED`, `TARGET CANCELLED`.

## What `TradeManager.run()` does

1. **Guards:** does nothing on trading holidays or after market close; waits for 09:15.
2. Creates today's folder `python-deploy/trades/<date>/`.
3. Creates a `ZerodhaTicker`, stores it on the broker login (so `Algo.stop_algo()` can close it), starts it and
   registers `ticker_listener`.
4. **Recovers state:** loads `trades.json` (if present) so trades survive an application restart, and
   re-subscribes their symbols.
5. **Main loop (every ~5 s until market close):**
   1. `fetch_and_update_all_trade_orders()` — pull the broker order book once and update every tracked order
      (status, fill qty, average price, trigger price).
   2. `track_and_update_all_trades()` — per active trade: square-off check, entry tracking, SL tracking,
      target tracking.
   3. `save_all_trade_to_file()` — persist `trades.json`.
   Exceptions in an iteration are logged and the loop continues.

## Triggering (event-driven)

`ticker_listener(tick)` runs on every tick:
- stores the last traded price per symbol (`symbol_to_cmp_map`);
- for each strategy, finds the not-yet-triggered `LONG` and `SHORT` trades on that symbol;
- asks the strategy `should_place_trade(trade, tick)`; if true, `execute_trade()` places the entry order and
  the trade becomes `ACTIVE` (`start_timestamp` recorded).

Trades are disabled (never triggered) when quantity is 0, the strategy's stop time has passed, or the strategy
already placed `max_trades_per_day`.

## Managing an active trade

| Step | Behaviour |
|---|---|
| **Entry tracking** | Copies `filled_qty` and average price from the entry order; marks the trade cancelled if the entry order was cancelled/rejected; updates `cmp` and P&L |
| **Stop-loss** | If `stop_loss != 0` and no SL order exists, places an **SL-M** order on the opposite side with the trigger at `stop_loss` |
| **SL filled** | Completes the trade with exit reason `SL HIT` (or `TRAIL SL HIT` if the SL had been trailed) and cancels the target order |
| **SL cancelled externally** | Completes the trade at the current market price with `SL CANCELLED` and cancels the target |
| **Trailing SL** | Asks the strategy for `get_trailing_sl(trade)`; if the new level is more favourable (higher for LONG, lower for SHORT) the SL order's trigger price is modified at the broker and `stop_loss` updated |
| **Target** | If `target != 0` and no target order exists, places a **LIMIT** order on the opposite side at `target` |
| **Target filled** | Completes with `TARGET HIT` and cancels the SL order |
| **Target cancelled externally** | Completes at market price with `TARGET CANCELLED`, cancels the SL |
| **Square-off** | When `now ≥ intraday_square_off_timestamp`: cancels a still-open entry order and the SL order, then converts the target order to MARKET (or places a new market exit order) |

### P&L
`Utils.calculate_trade_pnl()`:
- active trades → unrealised: `filled_qty × (cmp − entry)` for LONG, `filled_qty × (entry − cmp)` for SHORT;
- finished trades → realised using `exit`;
- `pnl_percentage = pnl × 100 / (entry × filled_qty)`.

## Persistence and recovery

- `trades.json` is rewritten each loop using `TradeEncoder` (serialises objects via `__dict__`, including the
  nested orders).
- On start, `convert_json_to_trade` / `convert_json_to_order` rebuild the objects. Strategies then call
  `get_all_trades_by_strategy()` to pick up their own trades again.

## Extension points
- A different broker: return its order manager from `TradeManager.get_order_manager()` and its ticker in
  `run()`.
- Extra risk checks: add them to `BaseStrategy.should_place_trade()` (applies to all strategies).
