# Changelog

All notable changes to the project are documented in this file.

## [Unreleased]

### Added

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
