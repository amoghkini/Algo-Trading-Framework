# Database

PostgreSQL is the system of record for users, brokers, access tokens, strategy parameters and the algo status.
Intraday trades and the instrument master are kept in JSON files instead (see
[Trading engine](trading-engine.md#persistence-and-recovery) and [Market data](market-data.md)).

**Code:** `src/database/`, DDL in `sql/`

## Setup

Run the scripts in `sql/` in this order:

1. `create_database.sql` — database `algo_trader_framework`
2. `create_schema.sql` — schema `algo_trader`
3. `users.sql`, `brokers.sql`, `access_tokens.sql`, `algo.sql`, `strategies.sql`

`strategies.sql` ends with a sample `INSERT` for the `SAMPLE` strategy, which `SampleStrategy` reads at start-up.

## Tables (schema `algo_trader`)

### `users`
| Column | Type | Notes |
|---|---|---|
| `id` | serial PK | |
| `email_id` | varchar(45) | unique, used for login |
| `password` | varchar(100) | `sha256_crypt` hash |
| `first_name`, `middle_name`, `last_name` | varchar(40) | |
| `user_name` | varchar(8) | generated at sign-up |
| `account_status` | varchar(20) | `Created` / `Activated` / `Deactivated` / `Deleted` |
| `account_creation_date`, `last_login_date` | bigint | epoch seconds |
| `mobile_no` | varchar(10) | unique |
| `date_of_birth`, `profile_pic`, `address1-3`, `city`, `state`, `country`, `pin_code` | | profile data |

### `brokers`
| Column | Type | Notes |
|---|---|---|
| `id` | serial PK | |
| `broker_id` | varchar(15) | **unique** client id |
| `broker_name` | varchar(45) | e.g. `Zerodha` |
| `user_name` | varchar(8) | owner |
| `password`, `totp_key`, `app_key`, `app_secret_key` | | broker credentials |
| `auto_login` | boolean | |
| `status` | varchar(20) | `Created` / `Activated` / `Deactivated` / `Deleted` |
| `login_status` | varchar(20) | `Logged in` / `Logged out` / `Yet to login` (added by an `ALTER`) |
| `broker_addition_date`, `last_login_date` | bigint | epoch seconds |

### `access_tokens`
Primary key `(broker_id, token_date)`; columns `broker_name`, `access_token`. One row per broker per day, upserted
on login and looked up for "today" to avoid re-logging in.

### `algo`
Single control row keyed by `name` (`Algo Trader`): `status`, `start_time`, `end_time`, `algo_start_reason`,
`algo_stop_reason`.

### `strategies`
`user_name`, `name`, `product_type`, `start_timestamp`, `stop_timestamp`, `square_off_timestamp`,
`target_percentage`, `stop_loss_percentage`, `capital`, `leverage`, `max_trades_per_day`, `is_fno`,
`capital_per_set`.

## Data-access layer

- `get_db()` returns a `PostgresSql` instance cached on Flask's request-scoped `g`, built from the environment
  variables `DB_HOST`, `DB_PORT`, `DB_SCHEMA` (the database name), `DB_USER`, `DB_PASSWORD`. The handle is
  created in the `before_request` hook and dropped in the app-context teardown.
- `PostgresSql` is a small psycopg2 wrapper with parameterised helpers:

  | Method | Purpose |
  |---|---|
  | `insert(schema, table, data)` | Insert a dict as a row |
  | `get_one(...)` / `get_all(...)` | Select with optional `where=("col = %s", [values])`, `order`, `limit`; rows come back as dicts |
  | `update(schema, table, data, where)` | Update columns from a dict |
  | `insert_or_update(schema, table, data, keys)` | `INSERT … ON CONFLICT (keys) DO UPDATE` — used for the algo row and access tokens |
  | `commit()` / `query()` | Transaction control and raw execution |

- `DatabaseSchema` and `DatabaseTables` hold the schema and table names so SQL identifiers are not scattered
  through the code.
- **MongoDB:** `database/mongo.py` and `mongo_connection.py` provide a MongoDB handle (`MONGO_*` variables), but
  the call in the request hook is commented out until Mongo is available in production.
