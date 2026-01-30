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
backend/app      # FastAPI backend
frontend/app.py  # Streamlit frontend
etl/export.py    # CSV export script
data/            # SQLite database (runtime)
```

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
