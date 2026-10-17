# Algo control

Starting, stopping and monitoring the trading algorithm from the UI.

**Code:** `src/algo/`, `src/restapis/{start_algo,stop_algo,status_algo}_api.py`,
`src/app/server_bootup_operations.py`

## Features

### Start
`GET /algo/start` → `AlgoMethods.start_algorithm()` → `Algo.start_algo()`:

1. Ignored (logged) if the algo is already running.
2. Fails with `BrokerNotFoundError` if no broker is logged in.
3. `Instruments.fetch_instruments()` loads the instrument master (see [Market data](market-data.md)).
4. Starts `TradeManager.run` in its own thread and waits 2 seconds for it to initialise.
5. Starts one thread per strategy: `SampleStrategy`, `BNFORB30Min`, `OptionSelling`, `ShortStraddleBNF`
   (see [Strategies](strategies.md)).
6. Updates the single row in `algo_trader.algo`: `status = Running`, `start_time = now (epoch)`,
   `algo_start_reason = "Manually started by user"`.

### Stop
`GET /algo/stop` → `Algo.stop_algo()` stops the broker ticker (closing the WebSocket) and marks the algo
`Stopped` with `end_time` and `algo_stop_reason = "Manually stopped by user"`.

### Status
`GET /algo/status` returns `{"status": "success", "algoStatus": "Running" | "Stopped"}` read from the `algo`
table. The dashboard can poll this endpoint.

### Start-up reset
On the first request after the application boots, `server_bootup_operations()`:
- upserts the algo row with status `Stopped` (so a crash never leaves a stale `Running`),
- sets all brokers to `Logged out`,
- declares the RabbitMQ exchange used by the [messaging engine](messaging.md).

### Reason constants
`algo/messages.py` defines the start/stop reasons, including `AUTO_STARTED_BY_SOD_PROCESS` and
`AUTO_STOPPED_BY_EOD_PROCESS` which are reserved for a future automatic start-of-day / end-of-day process.

## Response format

All three endpoints return JSON:

```json
{ "status": "success", "message": "Algo started successfully" }
{ "status": "fail",    "message": "Broker is not logged in. Not able to start the ticker service" }
```

## Endpoints

| Route | Method | Purpose |
|---|---|---|
| `/algo/start` | GET | Start engine and strategies |
| `/algo/stop` | GET | Stop ticker, mark stopped |
| `/algo/status` | GET | Current status |

## Related tables
`algo_trader.algo` — see [Database](database.md).
