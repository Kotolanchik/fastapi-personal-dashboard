# fastapi-personal-dashboard

MVP‑приложение для личной аналитики: сбор данных по здоровью, финансам, продуктивности и обучению с дашбордами, корреляциями, инсайтами и интеграциями.

---

## Как запустить приложение

### Вариант 1 — всё в Docker (рекомендуется)

Из корня проекта:

```bash
docker compose -f docker-compose.full.yml up --build
```

Поднимаются: **Postgres**, **Redis**, **backend** (миграции выполняются при старте), **React‑фронт**.

После запуска:
- **http://localhost:5173** — интерфейс (React)
- **http://localhost:8000** — API (FastAPI)
- **http://localhost:8000/docs** — Swagger

Остановка: `Ctrl+C`. При необходимости: `docker compose -f docker-compose.full.yml down`.

### Вариант 2 — режим разработки (hot reload)

Первый раз с пересборкой образов:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Дальше: `docker compose -f docker-compose.dev.yml up` (или `.\run-dev.ps1` в PowerShell, `run-dev.cmd` в CMD).

### Вариант 3 — локально без Docker

**Терминал 1 — backend:**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=sqlite:///./data/app.db
alembic upgrade head
uvicorn backend.app.main:app --reload --port 8000
```

**Терминал 2 — React:**

```bash
cd frontend-react
npm install
npm run dev
```

Интерфейс: **http://localhost:5173**, API: **http://localhost:8000**. Фронт по умолчанию использует `VITE_API_URL=http://localhost:8000`.

### Запуск одной командой (Windows)

| Режим   | CMD              | PowerShell       |
|--------|-------------------|------------------|
| Полный стек | `run.cmd`         | `.\run.ps1`      |
| Dev    | `run-dev.cmd`     | `.\run-dev.ps1`  |

---

## Возможности (MVP)

- **Четыре сферы**: Здоровье, Финансы, Продуктивность, Обучение — ручной ввод, CRUD, дашборды и временные ряды.
- **Здоровье**: несколько записей в день (day/morning/evening), шаги, пульс, тренировки; экспорт отчёта для врача (CSV).
- **Обучение**: справочник курсов/тем, привязка записей к курсу, тип источника (книга/курс/подкаст), streak (дни подряд).
- **Продуктивность**: задачи с дедлайнами и статусами, сессии фокуса (Pomodoro/deep_work), категория фокуса; дашборд продуктивности (лучшие дни/часы, тренды, разбивка по категориям).
- **Цели**: до 5 целей (лимит по сфере настраивается), прогресс по метрикам, цели «закончить курс»; архивация.
- **Аналитика**: корреляции, инсайты, рекомендации, еженедельный отчёт, кэширование в Redis (опционально).
- **Экспорт**: CSV (дневная сводка, по категориям), отчёт по здоровью за период.
- **Интеграции**: Google Fit (OAuth, шаги), Apple Health (импорт XML/ZIP), Open Banking (mock/токены); статус синка, последняя ошибка, «обновить сейчас», настройка метрик в дашборде.
- **Напоминания**: API и баннер на дашборде («заполни здоровье за вчера»); email‑напоминания (опционально, через воркер).
- **AI Assistant**: чат и инсайт по данным (OpenAI‑совместимый API, в т.ч. Ollama).
- **Аутентификация**: JWT, сброс пароля по email, роли user/admin; виджеты дашборда и настройки уведомлений в профиле.
- **Категории расходов**: маппинг категорий провайдера в свои (для Open Banking).
- **Биллинг**: каркас тарифов и подписок (оплата не подключена — демо).

---

## Архитектура

- **Backend**: FastAPI, SQLAlchemy, Alembic; SQLite или Postgres; опционально Redis; rate limit (slowapi).
- **Frontend**: React (Vite, TypeScript), TanStack Query, React Router, i18next (EN/RU).
- **DWH**: витрина данных (Alembic, Parquet, DuckDB, dbt) — отдельный контур.
- **Аналитика**: Pandas, NumPy, Statsmodels; рекомендации в `ml/`.

---

## Структура проекта

```
backend/
  app/
    api/
      deps.py              # зависимости (DB, auth)
      router.py            # агрегатор роутов
      routes/
        admin.py           # /admin (RBAC)
        analytics.py       # /analytics
        auth.py            # /auth (в т.ч. forgot/reset password)
        billing.py         # /billing
        export.py          # /export (CSV, health-report)
        finance.py         # /finance, /finance/category-mappings
        goals.py            # /goals
        health.py           # /health
        integrations.py    # /integrations (providers, sync, OAuth, Apple Health import)
        learning.py        # /learning, /learning/courses, /learning/streak
        llm.py              # /llm (chat, insight)
        productivity.py    # /productivity, /productivity/tasks, /productivity/sessions
        reminders.py        # /reminders
    core/
      config.py            # настройки (в т.ч. интеграции, rate limit, SMTP)
      constants.py         # роли, лимиты целей
      security.py          # JWT, хеширование паролей
    integrations/          # Google Fit, Apple Health, Open Banking
    llm/                   # клиент OpenAI-совместимого API
    ml/                    # рекомендации
    services/
      entries.py           # CRUD записей
      goals.py             # логика целей и прогресса
      users.py             # профиль, сброс пароля
      cache.py             # Redis
    tasks/
      reminder_emails.py   # рассылка напоминаний (cron)
    analytics.py           # корреляции, инсайты, weekly-report, productivity-dashboard
    database.py
    main.py                # FastAPI, rate limit
    models.py
    schemas.py
    utils.py
alembic/
  versions/                # миграции приложения
alembic.ini
frontend/
  app.py                   # Streamlit (альтернативный UI)
frontend-react/
  src/
    app/                   # App, providers
    features/              # dashboard, auth, entries (Health/Finance/Productivity/Learning),
                           # goals, integrations, settings, assistant, reports, billing
    shared/                # api (client, entries, goals, integrations, analytics, …), components, hooks, utils
    locales/               # en.json, ru.json
  package.json
dwh/
  alembic/, dbt/, duckdb/, etl/
  database.py, models.py
tests/                     # pytest (auth, entries, smoke)
.github/workflows/
  ci.yml                   # миграции + pytest + frontend lint
  docker-publish.yml      # сборка и публикация образов
.pre-commit-config.yaml   # ruff, ESLint
pyproject.toml            # ruff
requirements.txt
requirements-dev.txt
requirements-dwh.txt
docker-compose.full.yml    # Postgres + Redis + backend + frontend
docker-compose.dev.yml     # режим разработки (hot reload)
docker-compose.prod.yml
docker-compose.managed.yml # внешние Postgres/Redis
Dockerfile.backend
Dockerfile.frontend-react
.env.example
.env.prod.example
deploy/k8s/                # Kubernetes манифесты
deploy/helm/              # Helm chart
```

---

## Переменные окружения

Скопируйте `.env.example` в `.env`; для продакшена — `.env.prod.example`.

**Backend (основные):**
- `DATABASE_URL` — по умолчанию `sqlite:///./data/app.db`
- `SECRET_KEY` — обязательно в проде
- `CORS_ORIGINS` — по умолчанию `*`
- `ACCESS_TOKEN_EXPIRE_MINUTES` — по умолчанию 120
- `REDIS_URL` — опционально (кэш)
- `CACHE_TTL_SECONDS` — по умолчанию 300
- `RATE_LIMIT_DEFAULT` — по умолчанию `200/minute`

**Интеграции:**
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` — Google Fit OAuth
- `SYNC_MIN_INTERVAL_SECONDS` — минимум секунд между синками (по умолчанию 900)
- `MAX_IMPORT_FILE_SIZE_MB` — лимит размера файла Apple Health (по умолчанию 100)

**LLM:**
- `LLM_API_KEY` — OpenAI (или другой ключ)
- `LLM_BASE_URL` — для Ollama и др. (например `http://localhost:11434/v1`)
- `LLM_MODEL` — по умолчанию `gpt-4o-mini`

**Уведомления (email):**
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` — для рассылки напоминаний (запуск воркера: `backend.app.tasks.reminder_emails` по расписанию).

**React (Vite):**
- `VITE_API_URL` — по умолчанию `http://localhost:8000`

**DWH:**
- `DWH_DATABASE_URL` — по умолчанию `sqlite:///./data/dwh.db`

---

## Миграции (Alembic)

```bash
alembic upgrade head
```

Автогенерация:

```bash
alembic revision --autogenerate -m "описание"
```

Миграции DWH:

```bash
alembic -c dwh/alembic.ini upgrade head
```

---

## API (основное)

- **Auth**: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/forgot-password`, `POST /auth/reset-password`
- **Admin**: `GET /admin/users`, `PUT /admin/users/{id}/role`
- **Health**: `POST|GET|PUT|DELETE /health` (пагинация: `offset`, `limit`; заголовок `X-Total-Count`)
- **Finance**: `POST|GET|PUT|DELETE /finance`, `GET|POST|PUT|DELETE /finance/category-mappings`
- **Productivity**: `POST|GET|PUT|DELETE /productivity`, `GET|POST|PUT|DELETE /productivity/tasks`, `GET|POST /productivity/sessions`
- **Learning**: `POST|GET|PUT|DELETE /learning`, `GET|POST|PUT|DELETE /learning/courses`, `GET /learning/streak`
- **Goals**: `GET|POST|PUT|DELETE /goals`
- **Analytics**: `GET /analytics/correlations`, `GET /analytics/insights`, `GET /analytics/recommendations`, `GET /analytics/weekly-report`, `GET /analytics/productivity-dashboard`, trend/insight/weekday эндпоинты
- **Export**: `GET /export?category=...`, `GET /export/health-report?start_date=&end_date=`
- **Reminders**: `GET /reminders`
- **Integrations**: `GET /integrations/providers`, `GET|POST|PUT|DELETE /integrations`, `GET /integrations/sources/{id}/status`, `POST /integrations/{provider}/sync`, `GET /integrations/google_fit/oauth-url`, `POST /integrations/google_fit/oauth-callback`, `POST /integrations/apple-health/import`
- **Billing**: `GET /billing/plans`, `POST /billing/subscribe`, `GET /billing/subscription`
- **LLM**: `POST /llm/chat`, `GET /llm/insight`

---

## Аутентификация и роли (RBAC)

- Роли: `user`, `admin`. Все записи привязаны к пользователю.
- Админ: эндпоинты `/admin/*`. Назначение администратора в БД: `UPDATE users SET role='admin' WHERE email='...';`

---

## Production и CI/CD

**Docker Compose (production):**
- `docker compose -f docker-compose.prod.yml up --build`
- С внешними БД: `docker compose -f docker-compose.managed.yml up --build`

**Kubernetes:** манифесты в `deploy/k8s/` (namespace, configmap, secret, postgres, redis, migrate-job, backend, frontend, ingress). Для managed Postgres/Redis не применяйте postgres/redis, укажите URL в секрете.

**Helm:** `deploy/helm/personal-dashboard` — установка с `--set secrets.databaseUrl=...` и т.д.

**CI:** `.github/workflows/ci.yml` — миграции (`alembic upgrade head`), pytest (в т.ч. smoke), линт фронта. `.github/workflows/docker-publish.yml` — сборка и публикация образов в GHCR (`ghcr.io/<owner>/<repo>-backend`, `-frontend`).

---

## Инструменты разработки

```bash
pip install -r requirements-dev.txt
pre-commit install
ruff check .
pytest
```

Frontend: `cd frontend-react && npm run lint`.

---

## BigData витрины (DWH)

```bash
pip install -r requirements-dwh.txt
python dwh/etl/export_parquet.py
python dwh/duckdb/build_duckdb.py
DBT_PROFILES_DIR=dwh/dbt dbt run --project-dir dwh/dbt --vars '{"parquet_path":"dwh/parquet"}'
```

---

## Backlog / Планы

- Подключение реальной оплаты (Stripe и т.п.) для тарифов.
- PDF‑экспорт отчёта по здоровью (сейчас CSV).
- Расширение интеграций и ML‑рекомендаций.

История изменений — в [CHANGELOG.md](CHANGELOG.md).
