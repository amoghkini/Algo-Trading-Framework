# Configuration and deployment

## Configuration sources

| Source | Content |
|---|---|
| `config/server.json` | Non-secret server settings (below) |
| `config/holidays.json` | List of `YYYY-MM-DD` NSE trading holidays; weekends are handled in code |
| `.env` (copy of `.env.example`) | Secrets and connection settings, loaded with `python-dotenv` |
| `src/config/config.py` | Config classes, constants, and helpers to read the JSON files |

### `config/server.json`
| Key | Meaning | Default |
|---|---|---|
| `port` | HTTP port | `5000` |
| `deployDir` | Folder for generated runtime files (instruments, timestamps, trades) | `../python-deploy` |
| `logFileDir` | Log folder | `../logs` |
| `env` | `dev`, `test` or `prod` — selects `DevConfig` / `TestingConfig` / `ProdConfig` | `dev` |
| `sessionLifetime` | Session idle timeout in minutes | `30` |

Paths are relative to `src/`, so the app must be started from inside `src/`.

On start-up the app creates the log and deploy folders if they are missing and **exits** if `env` is not one of
the three valid values. `DEBUG` is on only when `env` is `dev`.

### Environment variables
| Variable | Used for |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` | PostgreSQL connection |
| `DB_SCHEMA` | Database name (`algo_trader_framework`) |
| `MONGO_HOST`, `MONGO_PORT`, `MONGO_DB` | MongoDB (currently disabled) |
| `EMAIL`, `EMAILPASS` | Gmail account used by the e-mail consumer |
| `TELEGRAMBOTTOKEN`, `TELEGRAMBOTCHATID` | Telegram alerts |
| `SECRET_KEY` | Flask session signing key (falls back to a placeholder — always set it) |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` | Passed into the container by `docker-compose.yaml` |

## Running locally

```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # fill in DB / e-mail values
# create the database objects with the scripts in sql/ (see database.md)
cd src
python main.py                                      # web app on http://localhost:5000
python consumer.py                                  # optional: e-mail worker (needs RabbitMQ)
```

Typical use: sign up → activate via e-mail link → log in → *Add broker* → *Login* on the broker →
*Start algo* from the dashboard.

## Docker

- `Dockerfile` — `python:3.8`, copies the repo to `/app`, installs `awscli` and the requirements, runs
  `python3 main.py` from `/app/src`.
- `docker-compose.yaml` — service `algo-trader`, publishes port **5000**, sets `TZ=Asia/Kolkata` (important:
  market-time logic uses local time), passes the AWS variables, bridge networking.

```bash
docker compose up --build
```

## CI/CD (`.github/workflows/main.yaml`)

Triggered by a push to `main` (README changes ignored):

1. **Continuous Integration** — placeholder lint and unit-test steps.
2. **Continuous Delivery** — configure AWS credentials from GitHub secrets, log in to Amazon ECR, build the
   image and push it as `:latest`.
3. **Continuous Deployment** — on a **self-hosted runner** (the EC2 host): pull the image, stop running
   containers, `docker run -d -p 5000:5000`, prune old images/containers.

Required GitHub secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `ECR_REPOSITORY_NAME`,
`AWS_ECR_LOGIN_URI`.

## Logging

`utils/logger.py` configures the root logger (file handler, DEBUG level) with a pipe-delimited format:
timestamp, level, process, thread, file, function, line, logger name, message. Logs go to
`logs/<YYYY-MM-DD>/app_<datetime>.log`. To read them from a running container use `docker exec -it <container> sh`
or mount the log folder as a volume (see `docs/questions.txt`).

## Error pages

Custom templates for HTTP 400, 403, 404, 405 and 500 are registered in `app/error_handlers.py`.
