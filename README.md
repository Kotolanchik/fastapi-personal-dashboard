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
        export.py         # /export endpoint
        finance.py        # /finance CRUD
        health.py         # /health CRUD
        learning.py       # /learning CRUD
        productivity.py   # /productivity CRUD
    core/
      config.py           # Environment settings
    services/
      entries.py          # Shared CRUD helpers
    analytics.py          # Correlations + insight generation
    database.py           # SQLAlchemy engine/session
    main.py               # FastAPI app entrypoint
    models.py             # SQLAlchemy models
    schemas.py            # Pydantic schemas
    utils.py              # Timezone normalization helpers
frontend/
  app.py                  # Streamlit UI (forms, charts, insights)
etl/
  export.py               # CLI export to CSV
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

# Run backend
uvicorn backend.app.main:app --reload --port 8000

# Run frontend
streamlit run frontend/app.py
```

Open Streamlit and set API URL to `http://localhost:8000`.

## Docker (optional)

```bash
docker compose up --build
```

Frontend: http://localhost:8501

You can also set `API_URL` to point Streamlit at a remote backend.

## Configuration

Backend environment variables:

- `DATABASE_URL` (default: `sqlite:///./data/app.db`)
- `CORS_ORIGINS` (default: `*`, comma-separated list)
- `APP_ENV` (default: `local`)

Frontend environment variables:

- `API_URL` (default: `http://localhost:8000`)

## API overview

- `POST /health`, `GET /health`, `PUT /health/{id}`, `DELETE /health/{id}`
- `POST /finance`, `GET /finance`, `PUT /finance/{id}`, `DELETE /finance/{id}`
- `POST /productivity`, `GET /productivity`, `PUT /productivity/{id}`, `DELETE /productivity/{id}`
- `POST /learning`, `GET /learning`, `PUT /learning/{id}`, `DELETE /learning/{id}`
- `GET /analytics/correlations`
- `GET /analytics/insights`
- `GET /export?category=health|finance|productivity|learning|daily`

## Next steps (roadmap)

- OAuth integrations (Google Fit, Apple Health)
- Bank transactions (Open Banking/Tinkoff)
- Mobile app (Kivy/Flutter)
- Subscription tiers (Stripe)
- Switch SQLite to Postgres in production
