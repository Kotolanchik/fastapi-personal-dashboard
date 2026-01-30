# fastapi-personal-dashboard

MVP‑приложение для личной аналитики: сбор данных по здоровью, финансам,
эффективности и обучению с дашбордами, корреляциями и инсайтами.

## Возможности (MVP)

- Ручной ввод данных по 4 сферам жизни
- Редактирование и удаление записей
- Дашборды и временные ряды
- Корреляции и 1–2 персональных инсайта
- Экспорт в CSV
- Поддержка часовых поясов
- Базовая аутентификация (JWT) и роли

## Архитектура

- **Backend**: FastAPI + SQLAlchemy + SQLite/Postgres
- **Frontend**: Streamlit (позже можно заменить на React/Vue)
- **DWH**: витрина данных с измерениями/фактами
- **Analytics**: Pandas + NumPy + Statsmodels

## Структура проекта

```
backend/
  app/
    api/
      deps.py             # зависимости (DB, auth)
      router.py           # агрегатор роутов
      routes/
        analytics.py      # /analytics
        auth.py           # /auth
        admin.py          # /admin (RBAC)
        export.py         # /export
        finance.py        # /finance CRUD
        health.py         # /health CRUD
        learning.py       # /learning CRUD
        productivity.py   # /productivity CRUD
    core/
      config.py           # настройки окружения
      constants.py        # роли и константы
      security.py         # хеширование паролей + JWT
    services/
      entries.py          # общие CRUD‑операции
      users.py            # управление пользователями
    analytics.py          # корреляции и инсайты
    database.py           # подключение к БД
    main.py               # точка входа FastAPI
    models.py             # модели SQLAlchemy
    schemas.py            # схемы Pydantic
    utils.py              # timezone‑хелперы
alembic/                  # миграции приложения
alembic.ini               # Alembic конфиг
frontend/
  app.py                  # Streamlit UI
etl/
  export.py               # экспорт CSV
dwh/
  alembic/                # миграции DWH
  alembic.ini             # DWH Alembic
  etl/
    load_dwh.py           # загрузка данных в DWH
    export_parquet.py     # экспорт в Parquet
  duckdb/
    build_duckdb.py       # сборка DuckDB витрины
  dbt/
    dbt_project.yml       # dbt проект
    profiles.example.yml  # пример профиля
    models/metrics/       # dbt модели
  database.py             # подключение DWH
  models.py               # DWH схема
tests/                    # pytest
.github/workflows/ci.yml  # CI
.pre-commit-config.yaml   # git hooks
pyproject.toml            # ruff config
requirements-dev.txt      # dev зависимости
requirements-dwh.txt      # bigdata стек
deploy/k8s/               # Kubernetes манифесты
docker-compose.yml        # локальная разработка
docker-compose.prod.yml   # production‑схема
```

## Быстрый старт (локально)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
uvicorn backend.app.main:app --reload --port 8000
streamlit run frontend/app.py
```

Откройте http://localhost:8501, зарегистрируйтесь и войдите.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

## Быстрый старт (Makefile)

```bash
make install
make migrate
make run-backend
```

Во втором терминале:

```bash
make run-frontend
```

## Production‑схема деплоя

### Docker Compose (production)

```bash
docker compose -f docker-compose.prod.yml up --build
```

### Kubernetes

```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/postgres.yaml
kubectl apply -f deploy/k8s/backend.yaml
kubectl apply -f deploy/k8s/frontend.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```

## Аутентификация и роли (RBAC)

- Роли: `user`, `admin`
- Все записи привязаны к пользователю
- Админские эндпоинты: `/admin/*`

Чтобы назначить администратора:

```sql
UPDATE users SET role='admin' WHERE email='admin@example.com';
```

## Переменные окружения

Скопируйте `.env.example` в `.env`, для продакшена используйте `.env.prod.example`.

**Backend:**
- `DATABASE_URL` (по умолчанию `sqlite:///./data/app.db`)
- `CORS_ORIGINS` (по умолчанию `*`)
- `SECRET_KEY` (обязательно в проде)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (по умолчанию 120)
- `AUTO_CREATE_TABLES` (по умолчанию false)

**Frontend:**
- `API_URL` (по умолчанию `http://localhost:8000`)

**DWH:**
- `DWH_DATABASE_URL` (по умолчанию `sqlite:///./data/dwh.db`)

## Миграции (Alembic)

```bash
alembic upgrade head
```

### Автогенерация миграций

```bash
alembic revision --autogenerate -m "описание"
```

DWH миграции:

```bash
alembic -c dwh/alembic.ini upgrade head
```

## BigData витрины (Parquet + DuckDB + dbt)

Установить стек:

```bash
pip install -r requirements-dwh.txt
```

Экспорт в Parquet:

```bash
python dwh/etl/export_parquet.py
```

Сборка DuckDB:

```bash
python dwh/duckdb/build_duckdb.py
```

dbt (пример):

```bash
DBT_PROFILES_DIR=dwh/dbt dbt run --project-dir dwh/dbt --vars '{"parquet_path":"dwh/parquet"}'
```

## Инструменты разработки

```bash
pip install -r requirements-dev.txt
pre-commit install
ruff check .
pytest
```

## API (основное)

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET /admin/users`, `PUT /admin/users/{id}/role`
- `POST /health`, `GET /health`, `PUT /health/{id}`, `DELETE /health/{id}`
- `POST /finance`, `GET /finance`, `PUT /finance/{id}`, `DELETE /finance/{id}`
- `POST /productivity`, `GET /productivity`, `PUT /productivity/{id}`, `DELETE /productivity/{id}`
- `POST /learning`, `GET /learning`, `PUT /learning/{id}`, `DELETE /learning/{id}`
- `GET /analytics/correlations`
- `GET /analytics/insights`
- `GET /export?category=health|finance|productivity|learning|daily`

## Перспективы развития

- Интеграции с Google Fit / Apple Health / Open Banking
- Автоматизированная аналитика и ML‑рекомендации
- Перенос DWH в BigQuery/Snowflake/ClickHouse
- Мобильное приложение и подписки
