# fastapi-personal-dashboard

MVP web application for collecting daily data across health, finance,
productivity, and learning. Includes a FastAPI backend (SQLite) and a
Streamlit frontend with dashboards, correlations, and insights.

## Features (MVP)

- Manual data entry forms for 4 life areas
- Edit/delete entries
- Dashboard charts (time series)
- Automatic correlations and 1-2 daily insights
- CSV export
- Timezone-aware timestamps and validation

## Project structure

```
backend/
  app/
    api/
      deps.py             # DB session dependency wiring
      router.py           # API router aggregator
      routes/
        analytics.py      # /analytics endpoints
        auth.py           # /auth endpoints
        export.py         # /export endpoint
        finance.py        # /finance CRUD
        health.py         # /health CRUD
        learning.py       # /learning CRUD
        productivity.py   # /productivity CRUD
    core/
      config.py           # Environment settings
      security.py         # Password hashing + JWT
    services/
      entries.py          # Shared CRUD helpers
      users.py            # User management helpers
    analytics.py          # Correlations + insight generation
    database.py           # SQLAlchemy engine/session
    main.py               # FastAPI app entrypoint
    models.py             # SQLAlchemy models
    schemas.py            # Pydantic schemas
    utils.py              # Timezone normalization helpers
alembic/                  # App migrations
alembic.ini               # App Alembic config
frontend/
  app.py                  # Streamlit UI (forms, charts, insights)
etl/
  export.py               # CLI export to CSV
dwh/
  alembic/                # DWH migrations
  alembic.ini             # DWH Alembic config
  etl/
    load_dwh.py           # Load app data into DWH
  database.py             # DWH connection
  models.py               # DWH schema (dims/facts)
tests/                    # Pytest suite
.github/workflows/ci.yml  # CI pipeline
.pre-commit-config.yaml   # Git hooks
pyproject.toml            # Ruff config
requirements-dev.txt      # Dev dependencies
data/                     # SQLite database (runtime)
Dockerfile.backend        # Backend container
Dockerfile.frontend       # Frontend container
docker-compose.yml        # Local multi-service setup
```

## Design notes (extensible + scalable)

- API routers are split by domain to keep modules small and easy to extend.
- Shared CRUD behaviors live in `services/` so new domains reuse logic.
- Configuration is centralized in `core/config.py` and pulled from env vars.
- Analytics is isolated, making it easy to add new models or forecasting later.
- Database access uses a dependency for clean request lifecycle handling.
- Auth is token-based and scopes all data to a user.

When scaling beyond MVP, consider:
- Migrations with Alembic (instead of `create_all`).
- Background jobs (Celery/RQ/Arq) for heavy analytics.
- Caching (Redis) for expensive insights.
- Postgres + read replicas, analytics warehouse, feature flags.
- Separate frontend (React/Vue) and deploy independently.

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run backend
uvicorn backend.app.main:app --reload --port 8000

# Run frontend
streamlit run frontend/app.py
```

Open Streamlit and set API URL to `http://localhost:8000`.

## Run on your PC (step-by-step)

1) Install Python 3.11+
2) Create a virtual environment:
   - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv && .\\.venv\\Scripts\\activate`
3) Install dependencies: `pip install -r requirements.txt`
4) Run app migrations: `alembic upgrade head`
5) Start backend: `uvicorn backend.app.main:app --reload --port 8000`
6) Start frontend (new terminal):
   `streamlit run frontend/app.py`
7) Open `http://localhost:8501`, register, and login.

## Docker (optional)

```bash
docker compose up --build
```

Frontend: http://localhost:8501

You can also set `API_URL` to point Streamlit at a remote backend.

## One-command setup (Makefile)

```bash
make install
make migrate
make run-backend
```

In a second terminal:

```bash
make run-frontend
```

Docker option:

```bash
make docker-up
```

## Environment (.env)

Copy `.env.example` to `.env` and update values as needed.

## Authentication

Create an account and login via the Streamlit sidebar. All data is scoped to
the authenticated user.

## Configuration

Backend environment variables:

- `DATABASE_URL` (default: `sqlite:///./data/app.db`)
- `CORS_ORIGINS` (default: `*`, comma-separated list)
- `APP_ENV` (default: `local`)
- `SECRET_KEY` (required for JWTs in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 120)
- `AUTO_CREATE_TABLES` (default: false)

Frontend environment variables:

- `API_URL` (default: `http://localhost:8000`)

DWH environment variables:

- `DWH_DATABASE_URL` (default: `sqlite:///./data/dwh.db`)

## Migrations

App database:

```bash
alembic upgrade head
```

DWH database:

```bash
alembic -c dwh/alembic.ini upgrade head
```

## DWH / Analytics Warehouse

The DWH schema uses dimensions and fact tables to store raw events by user/date.
Load app data into the warehouse with:

```bash
python dwh/etl/load_dwh.py
```

You can later push the DWH into BigQuery/Snowflake/DuckDB/Parquet for
large-scale analytics.

## Developer tooling

```bash
pip install -r requirements-dev.txt
pre-commit install
ruff check .
pytest
```

## API overview

- `POST /health`, `GET /health`, `PUT /health/{id}`, `DELETE /health/{id}`
- `POST /finance`, `GET /finance`, `PUT /finance/{id}`, `DELETE /finance/{id}`
- `POST /productivity`, `GET /productivity`, `PUT /productivity/{id}`, `DELETE /productivity/{id}`
- `POST /learning`, `GET /learning`, `PUT /learning/{id}`, `DELETE /learning/{id}`
- `GET /analytics/correlations`
- `GET /analytics/insights`
- `GET /export?category=health|finance|productivity|learning|daily`
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`

## Next steps (roadmap)

- OAuth integrations (Google Fit, Apple Health)
- Bank transactions (Open Banking/Tinkoff)
- Mobile app (Kivy/Flutter)
- Subscription tiers (Stripe)
- Switch SQLite to Postgres in production
