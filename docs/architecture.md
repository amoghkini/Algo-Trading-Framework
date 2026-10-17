# Architecture

This document describes how the Algo Trading Framework is put together: the layers, the runtime processes and
threads, the main flows, and the data model. All diagrams are [Mermaid](https://mermaid.js.org/) and render
natively on GitHub and in most Markdown viewers.

- [1. System overview](#1-system-overview)
- [2. Layered component view](#2-layered-component-view)
- [3. Runtime view (processes and threads)](#3-runtime-view-processes-and-threads)
- [4. Key flows](#4-key-flows)
- [5. Trade lifecycle](#5-trade-lifecycle)
- [6. Data model](#6-data-model)
- [7. Deployment](#7-deployment)
- [8. Design patterns used](#8-design-patterns-used)

---

## 1. System overview

A user manages everything through a Flask web UI. The web app stores users, brokers, strategies and the algo
status in PostgreSQL, logs in to a broker (Zerodha Kite), and starts the algo. Once started, the trading engine
streams live ticks from the broker, lets each strategy create trades, places and tracks orders, and persists
intraday trades to a JSON file.

```mermaid
flowchart LR
    User([Trader / Browser])

    subgraph App["Algo Trading Framework (Docker container, port 5000)"]
        Web["Flask web app<br/>UI + REST/JSON endpoints"]
        Engine["Algo + Trading engine<br/>(background threads)"]
    end

    PG[("PostgreSQL<br/>schema: algo_trader")]
    Files[("Local files<br/>python-deploy/ + logs/")]
    MQ{{"RabbitMQ<br/>exchange: messaging_engine"}}
    Consumer["consumer.py<br/>(separate process)"]
    Mail[/"Gmail SMTP"/]
    Telegram[/"Telegram Bot API"/]
    Kite[/"Zerodha Kite<br/>REST + WebSocket"/]

    User -->|HTTP| Web
    Web -->|SQL| PG
    Web -->|start / stop / status| Engine
    Web -->|login, orders, positions, holdings| Kite
    Web -->|publish email jobs| MQ
    MQ --> Consumer
    Consumer --> Mail
    Engine -->|REST: quotes, orders| Kite
    Kite -->|WebSocket ticks| Engine
    Engine -->|trades.json, instruments.json| Files
    Engine -->|strategy params| PG
    Web -.->|"not wired yet"| Telegram
```

---

## 2. Layered component view

The code under `src/` is organised so that **broker-specific code sits behind base classes** and
**strategies only talk to the trading engine**, never to the broker directly.

```mermaid
flowchart TB
    subgraph Presentation["Presentation layer"]
        Templates["templates/*.html<br/>static/main.css"]
        Forms["forms/ (Flask-WTF)"]
        RestAPIs["restapis/*_api.py<br/>(Flask MethodView classes)"]
        AppFactory["app/ (create_app, endpoints,<br/>error_handlers, bootup ops)"]
    end

    subgraph Domain["Domain / service layer"]
        UserM["user/UserMethods"]
        BrokerM["broker/BrokerMethods"]
        AlgoM["algo/AlgoMethods + Algo"]
        StratM["strategies/StrategyMethods"]
    end

    subgraph Core["Core"]
        Controller["core/Controller<br/>(holds active broker login)"]
        Quotes["core/Quotes"]
        Instruments["instruments/Instruments"]
    end

    subgraph Engine["Trading engine"]
        Strategies["strategies/<br/>BaseStrategy + 4 strategies"]
        TradeMgr["trading_engine/TradeManager<br/>Trade, TradeState, TradeExitReason"]
        OMS["order_management_system/<br/>BaseOrderManager → ZerodhaOrderManager"]
        Ticker["ticker/<br/>BaseTicker → ZerodhaTicker"]
    end

    subgraph BrokerAdapters["Broker adapters"]
        Login["login_management_system/<br/>BaseLogin → ZerodhaLogin, ZerodhaWebLogin"]
        TxnMgr["broker_transaction_management_system/<br/>BaseTransactionManager → ZerodhaTransactionManager"]
        KiteExt["broker_web_extenstions/KiteExt"]
    end

    subgraph Infra["Infrastructure"]
        DB["database/<br/>PostgresSql, MongoDB (disabled)"]
        Msg["messaging_engine/<br/>Producer, Consumer, Email, Telegram"]
        Config["config/ + config/*.json"]
        Utils["utils/ (Utils, TimeUtils, logger)"]
        Models["models/ (Quote, TickData, enums)"]
    end

    Templates --- RestAPIs
    Forms --- RestAPIs
    AppFactory --> RestAPIs
    RestAPIs --> UserM & BrokerM & AlgoM & StratM
    UserM --> DB
    UserM --> Msg
    BrokerM --> DB
    BrokerM --> Controller
    BrokerM --> TxnMgr
    StratM --> DB
    AlgoM --> DB
    AlgoM --> Instruments
    AlgoM --> TradeMgr
    AlgoM --> Strategies
    Controller --> Login
    Login --> KiteExt
    Quotes --> Controller
    Strategies --> Quotes
    Strategies --> TradeMgr
    Strategies --> DB
    TradeMgr --> OMS
    TradeMgr --> Ticker
    OMS --> Controller
    Ticker --> Controller
    Ticker --> Instruments
    Instruments --> Controller
    Core -.-> Utils
    Engine -.-> Utils
    Engine -.-> Models
```

### Module map

| Package | Responsibility |
|---|---|
| `app/` | `create_app()` factory, request hooks (session, DB handle), URL registration, error pages, one-time bootup operations |
| `restapis/` | One `MethodView` class per endpoint; thin: validate input, call a `*Methods` class, flash/redirect/return JSON |
| `forms/` | Flask-WTF forms (sign-up, login, profile, password change/reset, broker add/login) |
| `templates/`, `static/` | Jinja2 pages and CSS |
| `user/` | `User` entity, `UserStatus`, `UserMethods` (sign-up, login, tokens, passwords, profile, e-mails) |
| `broker/` | `Broker` entity, status enums, `BrokerMethods` (CRUD, login/logout, access tokens, orders/positions/holdings) |
| `core/` | `Controller` (the active broker login singleton) and `Quotes` (broker quote → internal `Quote`) |
| `login_management_system/` | Broker login strategies. `ZerodhaLogin` = official Kite API flow; `ZerodhaWebLogin` = user-id/password/TOTP or enctoken |
| `broker_web_extenstions/` | `KiteExt`, a `KiteConnect` subclass that talks to Kite's web front-end (enctoken auth) |
| `broker_transaction_management_system/` | Read-only account calls: profile (connection test), orders, positions, holdings |
| `algo/` | `Algo` (start/stop the engine), `AlgoMethods` (persist status), status/reason constants |
| `instruments/` | Download/cache the NSE + NFO instrument master; symbol ⇄ token lookup |
| `ticker/` | Live tick streaming (`ZerodhaTicker` over `KiteTicker`) and listener fan-out |
| `strategies/` | `BaseStrategy` template and the concrete strategies |
| `trading_engine/` | `TradeManager` (orchestrator), `Trade` entity, state/exit-reason enums, JSON encoder |
| `order_management_system/` | Order entity, input/modify params, broker order manager |
| `database/` | Thin psycopg2 wrapper (`PostgresSql`), table/schema name constants, Mongo wrapper (currently unused) |
| `messaging_engine/` | RabbitMQ producer/consumer, SMTP e-mail sender, Telegram sender |
| `config/` | Env configs (`DevConfig` etc.), loaders for `server.json`, `holidays.json`, `timestamps.json` |
| `utils/` | Market-time helpers, NSE price rounding, expiry/strike/symbol builders, P&L maths, logger setup |
| `models/` | Plain value objects and enums (`Quote`, `TickData`, `Direction`, `OrderType`, `OrderStatus`, `ProductType`, `Segment`) |
| `exceptions/` | Domain exception types for API, broker, strategy and user errors |

---

## 3. Runtime view (processes and threads)

There are two OS processes: the **web app** (`python main.py`) and the optional **consumer**
(`python consumer.py`). Starting the algo spawns additional threads **inside the web app process**.

```mermaid
flowchart TB
    subgraph P1["Process 1: python src/main.py (Flask, host 0.0.0.0:5000)"]
        direction TB
        Req["Flask request threads<br/>(UI + /algo/* + /oms/* endpoints)"]
        subgraph Started["Threads created by Algo.start_algo()"]
            TM["TradeManager.run<br/>loop every ~5 s:<br/>sync orders → track trades → save JSON"]
            WS["KiteTicker WebSocket thread<br/>(connect threaded=True)<br/>→ on_ticks → TradeManager.ticker_listener"]
            S1["SampleStrategy.run"]
            S2["BNFORB30Min.run"]
            S3["OptionSelling.run"]
            S4["ShortStraddleBNF.run"]
        end
        Req -->|"AlgoMethods.start_algorithm()"| Started
    end

    subgraph P2["Process 2: python src/consumer.py"]
        Cons["MessagingEngineConsumer<br/>blocks on queue message_priority1"]
    end

    S1 & S2 & S3 & S4 -->|"TradeManager.add_new_trade()"| TM
    WS -->|"tick → should_place_trade() → execute_trade()"| TM
    P1 -->|AMQP publish| MQ{{RabbitMQ}}
    MQ --> Cons
```

Each strategy thread wakes every 30 seconds (aligned to :00/:30), calls its `process()` and sleeps. Trade
**triggering** is event-driven: every incoming tick is offered to the strategies that own a not-yet-triggered
trade on that symbol.

### Application start-up sequence

```mermaid
sequenceDiagram
    participant M as main.py
    participant A as app.create_app()
    participant F as Flask
    participant DB as PostgreSQL
    participant MQ as RabbitMQ

    M->>A: create_app()
    A->>A: validate/create logs + deploy dirs
    A->>A: validate execution env (dev/test/prod)
    A->>F: configure (session lifetime, hooks, logger)
    A->>F: register_endpoints(), register_error_handlers()
    Note over F: first incoming request
    F->>DB: AlgoMethods.save_algo_data() (upsert algo row = Stopped)
    F->>DB: BrokerMethods.logout_all_brokers()
    F->>MQ: declare exchange "messaging_engine" (direct)
```

---

## 4. Key flows

### 4.1 Broker login (official Kite API flow, `api_with_broker_portal`)

```mermaid
sequenceDiagram
    actor U as User
    participant UI as /broker/login (LogInBrokerAPI)
    participant BM as BrokerMethods
    participant C as Controller
    participant ZL as ZerodhaLogin
    participant K as Zerodha Kite
    participant DB as PostgreSQL

    U->>UI: POST (broker id, login_method)
    UI->>BM: login_broker(args, broker)
    BM->>DB: read broker row (app_key, app_secret_key, totp_key)
    BM->>C: handle_broker_login()
    C->>DB: read today's access token (access_tokens)
    C->>ZL: login(args, broker_values)
    alt valid token exists
        ZL->>K: profile() — test connection
        K-->>ZL: OK
        ZL-->>C: no redirect (already logged in)
    else no/invalid token and no request_token
        ZL-->>UI: redirect to Kite login_url
        U->>K: authenticate (+2FA)
        K-->>UI: redirect back with request_token
        UI->>ZL: login(args with request_token)
        ZL->>K: generate_session(request_token, api_secret)
        K-->>ZL: access_token
    end
    C->>DB: upsert access_tokens (broker_id, token_date)
    BM->>DB: brokers.login_status = "Logged in"
    UI-->>U: flash success, redirect to /brokers
```

The other two login methods (`creds_with_enc_token`, `creds_without_enc_token`) go through `ZerodhaWebLogin`
and `KiteExt`: either an enctoken supplied by the user is used directly, or the framework posts user id +
password and a generated TOTP to Kite's web login endpoints and reads the `enctoken` cookie.

### 4.2 Starting the algo and executing a trade

```mermaid
sequenceDiagram
    actor U as User
    participant API as /algo/start
    participant AM as AlgoMethods
    participant AL as Algo
    participant I as Instruments
    participant TM as TradeManager
    participant T as ZerodhaTicker
    participant S as Strategy thread
    participant OM as ZerodhaOrderManager
    participant K as Zerodha Kite

    U->>API: GET /algo/start
    API->>AM: start_algorithm()
    AM->>AL: start_algo()
    AL->>I: fetch_instruments() (cache / download NSE+NFO)
    AL->>TM: start thread TradeManager.run
    TM->>TM: skip if holiday / market closed, wait for 09:15
    TM->>T: start_ticker() + register_listener()
    TM->>TM: load_all_trades_from_file() (crash recovery)
    AL->>S: start one thread per strategy
    AM->>AM: algo row → status Running
    loop every 30 s
        S->>K: Quotes.get_quote()
        S->>TM: add_new_trade(Trade state=CREATED)
        TM->>T: register_symbols([symbol])
    end
    K-->>T: ticks (WebSocket)
    T->>TM: ticker_listener(tick)
    TM->>S: should_place_trade(trade, tick)?
    S-->>TM: true (breakout / time / limits OK)
    TM->>OM: place_order(entry)
    OM->>K: place_order
    TM->>TM: trade.state = ACTIVE
    loop every ~5 s
        TM->>OM: fetch_and_update_all_order_details()
        TM->>OM: place SL / target orders, trail SL, square-off
        TM->>TM: save trades.json
    end
```

### 4.3 Account sign-up and e-mail verification

```mermaid
sequenceDiagram
    actor U as User
    participant API as /user/signup
    participant UM as UserMethods
    participant DB as PostgreSQL
    participant P as MessagingEngineProducer
    participant MQ as RabbitMQ
    participant C as consumer.py
    participant G as Gmail SMTP

    U->>API: POST sign-up form
    API->>UM: generate_user_name(), sign_up_user()
    UM->>DB: insert users (password hashed, status "Created")
    API->>UM: activate_account(email)
    UM->>P: publish {to, subject, link} (signed token, 1000 s)
    P->>MQ: exchange messaging_engine / key message_priority1
    MQ->>C: deliver
    C->>G: send e-mail
    U->>API: GET /user/verify/{token}
    API->>UM: decode_token, change_account_status(Activated)
```

---

## 5. Trade lifecycle

```mermaid
stateDiagram-v2
    [*] --> CREATED: Strategy.process() → TradeManager.add_new_trade()
    CREATED --> ACTIVE: tick satisfies should_place_trade()<br/>and entry order placed
    CREATED --> DISABLED: qty = 0 / past stop time /<br/>max trades per day reached
    ACTIVE --> COMPLETED: SL hit · trailing SL hit · target hit ·<br/>intraday square-off
    ACTIVE --> CANCELLED: entry order cancelled or rejected
    COMPLETED --> [*]
    CANCELLED --> [*]
    DISABLED --> [*]
```

While a trade is `ACTIVE`, `TradeManager` keeps three orders in sync: the **entry** order, a **stop-loss**
(SL-M) order and an optional **target** (LIMIT) order. Whichever of SL/target completes first causes the other
to be cancelled; at the strategy's square-off time the SL is cancelled and the position is closed with a market
order. See [Trading engine](features/trading-engine.md) for the details.

---

## 6. Data model

```mermaid
erDiagram
    USERS ||--o{ BROKERS : "owns (user_name)"
    USERS ||--o{ STRATEGIES : "owns (user_name)"
    BROKERS ||--o{ ACCESS_TOKENS : "daily token (broker_id)"

    USERS {
        serial id PK
        varchar email_id UK
        varchar user_name
        varchar password "sha256_crypt hash"
        varchar mobile_no UK
        varchar account_status "Created/Activated/Deactivated/Deleted"
        bigint account_creation_date
        date date_of_birth
    }
    BROKERS {
        serial id PK
        varchar broker_id UK
        varchar broker_name
        varchar user_name
        varchar password
        varchar totp_key
        varchar app_key
        varchar app_secret_key
        boolean auto_login
        varchar status
        varchar login_status "Logged in/Logged out/Yet to login"
    }
    ACCESS_TOKENS {
        varchar broker_id PK
        date token_date PK
        varchar broker_name
        varchar access_token
    }
    STRATEGIES {
        serial id PK
        varchar user_name
        varchar name
        varchar product_type
        time start_timestamp
        time stop_timestamp
        time square_off_timestamp
        numeric target_percentage
        numeric stop_loss_percentage
        integer capital
        smallint leverage
        smallint max_trades_per_day
        boolean is_fno
        integer capital_per_set
    }
    ALGO {
        varchar name PK
        varchar status "Running/Stopped"
        bigint start_time
        bigint end_time
        varchar algo_start_reason
        varchar algo_stop_reason
    }
```

`ALGO` is a single-row control table (keyed by the algo name from `config.py`). Non-relational state lives in
files under the deploy directory:

| File | Purpose |
|---|---|
| `python-deploy/instruments.json` | Cached NSE + NFO instrument master (refreshed after 24 h) |
| `python-deploy/timestamps.json` | Bookkeeping, e.g. `instrumentsLastSavedAt` |
| `python-deploy/trades/<YYYY-MM-DD>/trades.json` | All of the day's trades with their orders; reloaded on restart |
| `logs/<YYYY-MM-DD>/app_<datetime>.log` | Application log |

---

## 7. Deployment

```mermaid
flowchart LR
    Dev["Developer<br/>git push main"] --> GHA

    subgraph GHA["GitHub Actions: main.yaml"]
        CI["Continuous Integration<br/>(lint + tests are placeholders)"]
        CD1["Build Docker image<br/>push to Amazon ECR"]
        CD2["Continuous Deployment<br/>(self-hosted runner on EC2)"]
        CI --> CD1 --> CD2
    end

    CD1 --> ECR[("Amazon ECR")]
    CD2 -->|"docker pull + docker run -p 5000:5000"| EC2["EC2 host<br/>algo-trader container"]
    ECR --> CD2
```

See [Configuration & deployment](features/configuration-and-deployment.md).

---

## 8. Design patterns used

| Pattern | Where |
|---|---|
| Application factory | `app.create_app()` |
| Class-based views | every class in `restapis/` extends `flask.views.MethodView` |
| Template method | `BaseStrategy.run()` is fixed; subclasses supply `process()`, `should_place_trade()`, `get_trailing_sl()`, `can_trade_today()` |
| Adapter / strategy per broker | `BaseLogin`, `BaseOrderManager`, `BaseTicker`, `BaseTransactionManager` with Zerodha implementations; selection by broker name in `Controller`, `BrokerMethods`, `TradeManager` |
| Observer | `BaseTicker.register_listener()` / `on_new_ticks()` fan-out to `TradeManager.ticker_listener` |
| Singleton | each concrete strategy (`get_instance()`), `SingletonMeta` for the messaging producer, `Controller` static state |
| Facade / service layer | `UserMethods`, `BrokerMethods`, `AlgoMethods`, `StrategyMethods` isolate REST views from SQL and broker calls |
| Producer / consumer | RabbitMQ direct exchange for asynchronous e-mail delivery |
