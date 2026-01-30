# Changelog

All notable changes to the project are documented in this file.

## [Unreleased]

### Added

- **Analytics & insights (2.5)**  
  - **analytics.py**: Best/worst weekday for sleep and productivity (aggregation by weekday); linear trend over last 14/30 days for sleep, expenses, deep work; new insights: expenses grow faster than income, sleep worse after weekends (Monday vs rest), focus higher on days with ≥6h sleep; `trend_this_month()` (this month vs previous, ↑/↓); `insight_of_the_week()`; `weekday_and_trends_payload()` (best/worst weekday + trends_14/trends_30).  
  - **recommender.py**: Rules for expenses vs income trend (30-day slope), sleep worse after weekends (Monday), focus higher on days with ≥6h sleep.  
  - **API**: `GET /analytics/trend-this-month`, `GET /analytics/insight-of-the-week`, `GET /analytics/weekday-trends`; schemas TrendThisMonthResponse, InsightOfTheWeekResponse, WeekdayTrendsResponse.  
  - **Dashboard**: Block «Trend this month» (↑/↓ key metrics); «Insight of the week» above existing insights; «Last week in numbers» card with link to weekly report; «By weekday & recent trends» (best/worst weekday, 14/30-day trend directions).  
  - **Weekly report**: Page titled «Last week in numbers» (sums, averages, one insight); explicit link from dashboard.

- **Goals (2.1)**  
  - Backend: `user_goals` table, CRUD API `/goals`, progress computation (current vs target per sphere).  
  - Frontend: Goals in Settings (add/remove up to 2 goals), Goals progress block on Dashboard.  
  - Migration: `0005_add_user_goals.py`.

- **Onboarding (2.2)**  
  - Short first-run flow on Dashboard: modal explaining what the dashboard is (health, finance, productivity, learning) and suggesting to add the first entry (link to Health).  
  - Dismissal stored in `localStorage` (`lifepulse_onboarding_completed`).

- **Recommendations (2.3)**  
  - Extended `recommender.py`: more rules (low sleep, study consistency, focus vs deep work, income vs expenses), goal-aware recommendations (progress toward user goals).  
  - Analytics route passes user goals into recommender; cache key unchanged.

- **Weekly report (2.4)**  
  - Backend: `GET /analytics/weekly-report` — digest for last 7 days: summary by spheres (health, finance, productivity, learning) + one insight.  
  - Frontend: Weekly report page and nav link; displays period, sphere metrics, and insight.

---

## Previous implementations (pre-changelog)

- **MVP core**  
  - Manual data entry for 4 life spheres: Health, Finance, Productivity, Learning.  
  - CRUD for entries (create, list, update, delete) with date/timezone support.  
  - Dashboards and time-series charts (Recharts) for each sphere.  
  - Export to CSV (daily summary, all data, per category).

- **Analytics**  
  - Correlations between numeric metrics (Pandas).  
  - Insights (sleep vs productivity, sleep vs energy, finance vs wellbeing).  
  - Rule-based recommendations (sleep–energy, deep work–wellbeing, food spend–wellbeing).  
  - Optional Redis caching for correlations, insights, recommendations.

- **Auth & users**  
  - JWT authentication (register, login, `/auth/me`).  
  - Profile update (name, default timezone) and change password.  
  - RBAC: `user` and `admin` roles; admin endpoints under `/admin/*`.

- **Integrations (scaffold)**  
  - Providers list, connect, sync (Google Fit, Apple Health, Open Banking).  
  - Data sources and sync jobs models; token storage.

- **Billing (scaffold)**  
  - Plans and subscriptions models; subscribe and subscription endpoints.  
  - Billing page in React.

- **Frontend**  
  - React (Vite, TypeScript), TanStack Query, React Router.  
  - Landing, Login, Register, Dashboard, Health/Finance/Productivity/Learning pages, Integrations, Billing, Settings.  
  - Layout with sidebar nav, API error banner, toasts.  
  - Legal: Privacy and Terms pages.

- **Backend**  
  - FastAPI, SQLAlchemy, Alembic.  
  - SQLite/Postgres; optional Redis.  
  - Migrations: app schema, roles, integrations & billing, default timezone.

- **DWH & data**  
  - DWH schema (Alembic), Parquet export, DuckDB build, dbt models (finance/health summary).  
  - ETL and export utilities.

- **DevOps**  
  - Docker Compose (dev, prod, managed Postgres/Redis), Dockerfiles (backend, frontend, React).  
  - Kubernetes manifests and Helm chart.  
  - CI (e.g. pytest) and Docker publish workflow.
