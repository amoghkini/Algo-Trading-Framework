# Algo Trading Framework — Documentation

A Flask-based framework for low- to medium-frequency algorithmic trading on the Indian markets (NSE / NFO),
currently integrated with **Zerodha Kite**. Users register, connect a broker account, and run strategies that
create, trigger and manage trades automatically, while the web UI shows brokers, strategies, orders, positions
and holdings.

> This documentation describes the code as committed in git `HEAD`.

## Start here

| Document | What it covers |
|---|---|
| **[Architecture](architecture.md)** | System diagram, layered components, threads/processes, sequence diagrams, trade lifecycle, ER diagram, deployment |

## Feature documentation

| Feature | Document |
|---|---|
| Accounts: sign-up, e-mail activation, login, password reset, profile | [user-management.md](features/user-management.md) |
| Brokers: add, login (3 methods), logout, orders / positions / holdings | [broker-management.md](features/broker-management.md) |
| Starting, stopping and monitoring the algo | [algo-control.md](features/algo-control.md) |
| Strategy framework and the four bundled strategies | [strategies.md](features/strategies.md) |
| Trade manager: triggering, SL, target, trailing SL, square-off, recovery | [trading-engine.md](features/trading-engine.md) |
| Order placement / modification / sync | [order-management.md](features/order-management.md) |
| Live ticks, quotes, instrument master | [market-data.md](features/market-data.md) |
| RabbitMQ, e-mail and Telegram | [messaging.md](features/messaging.md) |
| PostgreSQL schema and data-access layer | [database.md](features/database.md) |
| Config files, environment variables, Docker, CI/CD, logging | [configuration-and-deployment.md](features/configuration-and-deployment.md) |
| Routes, templates, forms, request hooks | [web-ui-and-api.md](features/web-ui-and-api.md) |
| Market calendar, symbol builders, P&L, exceptions | [utilities.md](features/utilities.md) |
| What is unfinished, known bugs, security notes | [status-and-known-issues.md](features/status-and-known-issues.md) |

## Feature summary

- **User accounts** with e-mail verification, strong-password rules, password reset and profile pictures.
- **Broker connectivity** to Zerodha through the official API flow, credentials + generated TOTP, or an enctoken,
  with a per-day access-token cache.
- **Algo control** from the dashboard (start / stop / status), persisted in the database.
- **Pluggable strategies**: equity breakout, Bank Nifty opening-range breakout, Nifty option selling, Bank Nifty
  short straddle with trailing stop-loss.
- **Trading engine**: tick-driven triggering, automatic SL and target orders, trailing SL, intraday square-off,
  P&L tracking and crash recovery from a daily JSON file.
- **Broker-agnostic design**: login, order, ticker and transaction-manager base classes with Zerodha adapters.
- **Account views**: orders, positions, holdings.
- **Asynchronous notifications** via RabbitMQ (e-mail) and a Telegram sender.
- **Market calendar** with holidays, weekly / monthly expiry and symbol generation for futures and options.
- **Ops**: Docker image, docker-compose, GitHub Actions → ECR → EC2 deployment, daily rotating log folders.

## Repository layout

```
.
├── config/                 server.json, holidays.json
├── docs/                   this documentation (+ the author's working notes: notes.txt, to do, …)
├── sql/                    DDL for database, schema and tables
├── src/
│   ├── main.py             web app entry point
│   ├── consumer.py         e-mail consumer entry point
│   ├── app/                app factory, endpoints, error handlers, bootup operations
│   ├── restapis/           one MethodView per endpoint
│   ├── user/ broker/ algo/ domain services
│   ├── core/               Controller (active broker login), Quotes
│   ├── login_management_system/  broker_web_extenstions/  broker_transaction_management_system/
│   ├── strategies/ trading_engine/ order_management_system/ ticker/ instruments/
│   ├── database/ messaging_engine/ config/ utils/ models/ exceptions/ common/
│   └── templates/ static/ forms/
├── tests/
├── Dockerfile  docker-compose.yaml  requirements.txt  .env.example
└── .github/workflows/main.yaml
```

## Quick start

See [Configuration & deployment → Running locally](features/configuration-and-deployment.md#running-locally).
