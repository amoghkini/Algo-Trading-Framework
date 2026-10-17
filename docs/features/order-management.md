# Order management

A broker-neutral layer for placing, modifying, cancelling and synchronising orders.

**Code:** `src/order_management_system/`, `src/models/{order_type,order_status,product_type,direction}.py`

## Components

| Class | Role |
|---|---|
| `BaseOrderManager` | Interface: `place_order`, `modify_order`, `modify_order_to_market`, `cancel_order`, `fetch_and_update_all_order_details`, plus converters to broker enums. Takes the broker handle from `Controller` |
| `ZerodhaOrderManager` | Kite implementation (regular variety) |
| `OrderInputParams` | Request to place an order: symbol, direction, product type, order type, price, trigger price, quantity, `is_fno` |
| `OrderModifyParams` | Requested changes: new quantity / price / trigger price / order type |
| `Order` | The tracked order: ids, status, quantities, prices, timestamps and the broker's message |

## Supported values

| Concept | Values |
|---|---|
| Direction | `LONG` (BUY), `SHORT` (SELL) |
| Product type | `MIS` (intraday), `NRML` (overnight F&O), `CNC` (delivery) |
| Order type | `LIMIT`, `MARKET`, `SL_MARKET` (Kite SL-M), `SL_LIMIT` (Kite SL) |
| Order status | `OPEN`, `COMPLETE`, `OPEN PENDING`, `VALIDATION PENDING`, `PUT ORDER REQ RECEIVED`, `TRIGGER PENDING`, `REJECTED`, `CANCELLED` |
| Segment | `EQUITY`, `FNO`, `CURRENCY`, `COMMADITY` (enum defined in `models/segment.py`) |

## Behaviour

- **Place:** equity orders go to `NSE`, F&O orders (`is_fno`) to `NFO`. The returned `Order` carries the broker
  order id and place/update timestamps. Failures are logged and re-raised so `TradeManager` can react.
- **Modify:** only fields greater than zero / not `None` are sent. Used for trailing stop-loss
  (new trigger price) and for turning a resting target order into a market order at square-off.
- **Cancel:** cancels by order id.
- **Synchronise:** one `orders()` call fetches the whole order book; each tracked order is matched by id and
  refreshed (quantity, filled, pending, status, price, trigger price, average price). A cancelled order with a
  non-zero fill quantity is treated as completed, because the engine cancels the pending remainder at the
  strategy stop time.

## Adding a broker
Subclass `BaseOrderManager`, implement the five operations and the three `convert_to_broker_*` methods, and
return it from `TradeManager.get_order_manager()`.

See also [Trading engine](trading-engine.md) for how and when `TradeManager` calls this layer.
