# История изменений

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).  
Версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

**Релизов пока не было.** Ниже — текущее состояние продукта (не выпущено).

---

## [Не выпущено]

### Добавлено

- **Ядро продукта**
  - Ручной ввод данных по четырём сферам: Здоровье, Финансы, Продуктивность, Обучение.
  - CRUD для записей (создание, список, обновление, удаление) с поддержкой даты и часового пояса.
  - Дашборды и графики временных рядов (Recharts) по каждой сфере.
  - Экспорт в CSV (дневная сводка, все данные, по категориям).
  - React (Vite, TypeScript), TanStack Query, React Router; Landing, Login, Register, Dashboard, страницы Health / Finance / Productivity / Learning, Integrations, Billing, Settings; Layout с боковой навигацией, баннер ошибок API, тосты; Privacy и Terms.

- **Аутентификация и пользователи**
  - JWT (регистрация, вход, `/auth/me`).
  - Обновление профиля (имя, часовой пояс по умолчанию), смена пароля.
  - Роли `user` и `admin`; админ-эндпоинты в `/admin/*`.

- **Backend и инфраструктура**
  - FastAPI, SQLalchemy, Alembic; SQLite / Postgres; опционально Redis.
  - Миграции: схема приложения, роли, интеграции и биллинг, часовой пояс по умолчанию, цели, архивация целей.
  - DWH: схема (Alembic), экспорт в Parquet, сборка DuckDB, dbt-модели (сводки по финансам и здоровью); ETL и утилиты экспорта.
  - Docker Compose (dev, prod, managed Postgres/Redis), Dockerfile для backend, frontend и React; манифесты Kubernetes и Helm chart; CI (pytest), workflow публикации Docker-образов.

- **Аналитика**
  - Корреляции между числовыми метриками (Pandas).
  - Инсайты: сон vs продуктивность, сон vs энергия, финансы vs самочувствие; расширения: расходы vs доход, сон после выходных, фокус при ≥6 ч сна.
  - Рекомендации: сон–энергия, глубокая работа–самочувствие, траты на еду–самочувствие; правила по тренду расходов vs дохода (30 дней), сон после выходных, фокус при ≥6 ч сна; рекомендации с учётом целей пользователя.
  - API: корреляции, инсайты, рекомендации, trend-this-month, insight-of-the-week, weekday-trends, weekly-report.
  - Опциональное кэширование в Redis для корреляций, инсайтов и рекомендаций.

- **Цели (Goals)**
  - Backend: таблица `user_goals`, CRUD API `/goals`, расчёт прогресса (текущее значение vs цель по сфере); миграции `0005_add_user_goals`, `0006_add_archived_to_user_goals`.
  - Лимит активных целей: 5; архивация (`archived`); период прогресса: `GET /goals?period=7d|month|deadline` и `include_archived`.
  - Frontend: управление целями в Настройках (до 5 целей, выбор целевой метрики по сфере, дедлайн); страница Goals с просмотром прогресса, выбором периода и «Показать архивные».
  - Редактирование на странице Goals: модальное окно (название, сфера, метрика, целевое значение, дедлайн), кнопки «В архив» / «Восстановить», удаление.
  - Дедлайны: отображение «осталось N дн.» при приближении (≤14 дней), «дедлайн прошёл»; прогресс-бары (цвет по проценту); на дашборде — бейджи «Почти достигнута!» (≥90%) и «Сильно отстаёте» (&lt;50% при дедлайне ≤14 дн.).

- **Еженедельный отчёт и расширенная аналитика**
  - `GET /analytics/weekly-report` — дайджест за последние 7 дней (сводка по сферам, один инсайт).
  - Страница «Weekly report» в навигации; блоки «Trend this month», «Insight of the week», «By weekday & recent trends» на дашборде; карточка «Last week in numbers» со ссылкой на отчёт.

- **Онбординг и напоминания**
  - Онбординг: модальное окно при первом запуске (объяснение сфер, предложение добавить первую запись в Health); закрытие в `localStorage` (`lifepulse_onboarding_completed`).
  - Напоминание о неактивности: при входе на дашборд проверка давности последней записи; если записей нет или последняя старше 3 дней — модальное окно «You haven't logged in X days. Log today?» с кнопками «Log today» и «Later».

- **Локализация (EN / RU)**
  - i18next, react-i18next, i18next-browser-languagedetector; ресурсы `src/locales/en.json` и `src/locales/ru.json`.
  - Переключатель языка в шапке Layout; сохранение в `localStorage` (`lifepulse_lang`).
  - Все пользовательские строки через `t()`; даты в еженедельном отчёте по текущей локали.

- **AI Assistant (LLM)**
  - Backend: модуль `llm`, клиент OpenAI-совместимого API (OpenAI, Ollama и др.); конфиг `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`.
  - API: `POST /llm/chat` (чат с контекстом из аналитики), `GET /llm/insight`.
  - Frontend: страница «AI Assistant», чат с подстановкой контекста дашборда, кнопка «Один инсайт по данным»; тосты при ошибке (LLM не настроен).
  - Зависимость: `openai>=1.0.0`; примеры в `.env.example` и `docker-compose.full.yml`.

- **Здоровье (Health) — расширения**
  - Несколько записей в день: поле `entry_type` (day / morning / evening), одна запись на день по-прежнему поддерживается.
  - Доп. метрики: `steps`, `heart_rate_avg`, `workout_minutes` (опционально).
  - Аналитика: тренд веса в «Trend this month» и «Weekday trends», сон по дням недели (best/worst weekday), учёт новых метрик в сводках.
  - Экспорт: `GET /export/health-report?start_date=&end_date=` — CSV по периоду для врача (имя файла `health_report_YYYY-MM-DD_YYYY-MM-DD.csv`).
  - Цели: поддержка целевых метрик `steps` и `workout_minutes`.

- **Обучение (Learning) — расширения**
  - Справочник курсов/тем: таблица `learning_courses`, CRUD API `/learning/courses` (title, kind: course/book/topic).
  - В записях обучения: привязка к курсу (`course_id`), тип источника (`source_type`: book / course / podcast).
  - Streak: `GET /learning/streak` — текущая серия дней подряд с хотя бы одной записью обучения (`current_streak_days`, `last_activity_date`).

- **Продуктивность (Productivity) — расширения**
  - Задачи: таблица `productivity_tasks`, CRUD API `/productivity/tasks` (title, status: open/done/cancelled, due_at); при смене статуса на done проставляется `completed_at`.
  - Привязка «tasks_completed» к реальным задачам: таблица `productivity_entry_completed_tasks` (entry_id, task_id); при создании/обновлении записи продуктивности можно передать `completed_task_ids` — список ID задач, выполненных за день; в ответе запись содержит `completed_task_ids`; при передаче списка `tasks_completed` выставляется равным количеству привязанных задач.
  - Категория фокуса: поле `focus_category` в записях продуктивности (code / writing / meetings / other) для аналитики «на что уходит время».
  - Сессии фокуса (Pomodoro/таймеры): таблица `focus_sessions`, `POST /productivity/sessions`, `GET /productivity/sessions` (duration_minutes, session_type: pomodoro/deep_work); агрегация по дате в часы глубокой работы.
  - Агрегация сессий в часы глубокой работы: в дневной сводке (`build_daily_dataframe`) добавлены колонки `session_deep_work_hours` (сумма длительностей сессий по дню) и `total_deep_work_hours` (запись + сессии); еженедельный отчёт по продуктивности при наличии сессий включает `session_deep_work_total` и `total_deep_work_total`.
  - Аналитика по категориям фокуса: агрегация записей по `focus_category` (сумма `deep_work_hours` по категории) — «на что уходит время».
  - Дашборд продуктивности: `GET /analytics/productivity-dashboard` — лучшие/худшие дни по глубокой работе (в т.ч. `total_deep_work_hours`), тренды 14/30 дней, суммарные часы из сессий, лучшие часы дня по сессиям фокуса (`top_hours`), разбивка по категориям фокуса (`focus_by_category`), один инсайт (связь с сном/обучением из существующих рекомендаций).

- **Напоминания**
  - API напоминаний: `GET /reminders` — список напоминаний (тип, should_remind, message); напоминание «заполни здоровье за вчера» при отсутствии записи за вчера.

- **Миграции**
  - `0007_health_learning_productivity_extensions`: health (entry_type, steps, heart_rate_avg, workout_minutes), learning_courses + course_id/source_type в learning_entries, productivity_tasks + focus_category в productivity_entries, focus_sessions.
  - `0008_productivity_entry_completed_tasks`: таблица связи записей продуктивности с выполненными задачами (entry_id, task_id).
  - `0009_integrations_last_error_sync_settings`: в data_sources добавлены last_error, sync_settings.
  - `0010_forgot_password_sync_job_source`: в users — password_reset_token, password_reset_expires; в sync_jobs — data_source_id (FK на data_sources).

- **Интеграции (расширения)**
  - Модели: в `data_sources` добавлены `last_error` (последняя ошибка синка), `sync_settings` (JSON: какие метрики подмешивать, напр. `{"health": ["steps", "sleep"], "finance": ["*"]}`).
  - **Google Fit**: OAuth (GET `/integrations/google_fit/oauth-url` → редирект пользователя; POST `/integrations/google_fit/oauth-callback` с `code` → обмен на токены, создание/обновление DataSource). Вызов Fitness API (шаги за последние 30 дней), маппинг в `HealthEntry` (поле `steps`); при наличии `refresh_token` — обновление `access_token` перед запросом. Конфиг: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`.
  - **Apple Health**: импорт по файлу (POST `/integrations/apple-health/import`): загрузка `export.xml` или ZIP с `export.xml`; парсинг Record (шаги, сон, пульс, вес), агрегация по дню, создание/обновление `HealthEntry`. Без OAuth (импорт вручную).
  - **Open Banking**: заглушка заменена на mock: `fetch()` возвращает тестовые транзакции, категоризация (food, transport, health, income, other), агрегация по дню в `FinanceEntry`. Реальный API банка подключается через токены в DataSource.
  - Синхронизация: при успехе обновляются `last_synced_at` и сбрасывается `last_error`; при ошибке — запись в `last_error` и в `SyncJob.message`. Ограничение частоты: `SYNC_MIN_INTERVAL_SECONDS` (по умолчанию 900), при более частом вызове POST `.../sync` возвращается последний job без нового запуска.
  - API статуса: GET `/integrations/sources/{id}/status` — источник, последний job (статус, сообщение), `last_error`. На фронте: статус синка, последняя ошибка, кнопка «обновить сейчас» (POST `/{provider}/sync`). Опционально: выбор метрик в `sync_settings` (какие метрики из интеграции подмешивать в дашборд).
  - Миграция: `0009_integrations_last_error_sync_settings` — колонки `last_error`, `sync_settings` в `data_sources`.

- **Биллинг (заготовки)**
  - Модели планов и подписок, эндпоинты subscribe/subscription, страница Billing; пометка «Billing is in demo mode. No real charges.»; в README — что оплата пока не подключена.

- **Ревью продукта (лендинг и UX)**
  - Лендинг: hero на выгоды и ЦА; блок про бесплатный аккаунт и премиум «coming soon»; социальное доказательство.
  - При залогиненном пользователе `/` перенаправляет на `/dashboard`.
  - index.html: meta description и Open Graph.
  - README: развёртывание одной командой (миграции при старте backend), Backlog (подключение оплаты).

- **Функционал по ревью (REVIEW.md 11–15)**
  - **Forgot password**: модель User — поля `password_reset_token`, `password_reset_expires`; сервисы `request_password_reset`, `reset_password_by_token`; API `POST /auth/forgot-password` (email), `POST /auth/reset-password` (token, new_password). Миграция `0010_forgot_password_sync_job_source`.
  - **Валидация entry_type**: в Health допустимы только `day` / `morning` / `evening` — схемы `HealthEntryBase` и `HealthEntryUpdate` с `Literal["day", "morning", "evening"]`.
  - **Лимит целей по сфере**: константа `GOAL_MAX_PER_SPHERE` (по умолчанию 2); при создании цели проверка количества активных целей по сфере; API возвращает 400 при превышении.
  - **Пагинация списков**: `GET /health`, `/finance`, `/productivity`, `/learning` принимают `offset` (по умолчанию 0) и `limit` (по умолчанию 50, макс. 200); в ответе заголовок `X-Total-Count` с общим числом записей по фильтрам.
  - **Связь SyncJob с DataSource**: в модель SyncJob добавлен `data_source_id` (FK на data_sources, nullable); миграция `0010_forgot_password_sync_job_source`; при создании job передаётся `data_source_id`; GET `/integrations/sources/{id}/status` фильтрует последний job по `data_source_id`.

- **Функционал по ревью (REVIEW.md 19–27): новые поля в UI и API-клиент**
  - **Типы в entries.ts**: `HealthEntry` — `entry_type`, `steps`, `heart_rate_avg`, `workout_minutes`; `ProductivityEntry` — `focus_category`, `completed_task_ids`; `LearningEntry` — `course_id`, `source_type`. Параметры пагинации в `fetchEntries` (start_date, end_date, offset, limit).
  - **DataSource**: в типе добавлены `user_id`, `last_error`, `sync_settings`.
  - **API-клиент**: добавлены вызовы `/learning/streak`, `/learning/courses` (CRUD), `/reminders`, `/export/health-report`, `/analytics/productivity-dashboard`, `/integrations/sources/:id/status`, `/integrations/google_fit/oauth-url`, `/integrations/google_fit/oauth-callback`, `/integrations/apple-health/import`; типы для ответов (LearningCourse, RemindersResponse, ProductivityDashboardResponse, SourceStatusResponse, AppleHealthImportResponse).
  - **HealthPage**: отображение и редактирование `entry_type` (day/morning/evening), `steps`, `heart_rate_avg`, `workout_minutes`.
  - **LearningPage**: `course_id` (выбор из списка курсов по API), `source_type` (book/course/podcast/other); загрузка курсов через `listLearningCourses`.
  - **ProductivityPage**: отображение и редактирование `focus_category` (code/writing/meetings/other).
  - **EntriesPage**: поддержка поля типа `select` (options, valueType number для course_id); значение по умолчанию для select при создании записи.
  - **Локализация**: подписи для entry_type, steps, heart_rate_avg, workout_minutes, focus_category, course, source_type (en/ru).

- **Функционал по ревью (REVIEW.md 28–34): интеграции на фронте, локализация, зависимости**
  - **OAuth Google Fit**: кнопка «Connect with Google Fit» — запрос oauth-url, редирект на Google; маршрут `/integrations/oauth-callback` для обработки `?code=...`, обмен кода через `POST /integrations/google_fit/oauth-callback`, редирект на `/integrations` с тостом об успехе/ошибке.
  - **Apple Health**: загрузка файла (export.xml или .zip), вызов `POST /integrations/apple-health/import`, отображение результата (импортировано записей).
  - **Интеграции**: колонка «Last error» в таблице источников; кнопка «Update now» для запуска синхронизации; настройка `sync_settings` (JSON: какие метрики подмешивать) — раскрываемая форма на каждую запись с textarea и сохранением через `PUT /integrations/{id}`.
  - **Локализация**: ключи для интеграций (connectGoogleFit, uploadAppleHealth, lastError, updateNow, syncSettings, oauth callback, import и др.), для learning (courses, streak), reminders, export (healthReport) в en.json и ru.json.
  - **Зависимости**: в `frontend-react/package.json` в dependencies добавлены `i18next`, `react-i18next`, `i18next-browser-languagedetector`.

- **Функционал по ревью (REVIEW.md 38–59): приоритет высокий**
  - **Фронт для новых полей**: Learning — секция «Мои курсы» с CRUD (список курсов, добавление, редактирование, удаление); Productivity — секция «Задачи» (список с дедлайнами и статусами, добавление задачи, «Выполнено», удаление) и секция «Сессии фокуса (Pomodoro)» (длительность, тип pomodoro/deep_work, кнопка «Добавить сессию»). API-клиент: `productivity.ts` — listProductivityTasks, createProductivityTask, updateProductivityTask, deleteProductivityTask, listFocusSessions, createFocusSession.
  - **Напоминания**: при заходе на дашборд вызов `GET /reminders`; при наличии напоминания «заполни здоровье за вчера» (health_yesterday, should_remind) — баннер с кнопкой «Заполнить» и ссылкой на `/health?date=YYYY-MM-DD` (вчера). EntriesPage поддерживает `initialDate` из query-параметра для предзаполнения даты.
  - **Экспорт отчёта по здоровью**: на странице Health карточка «Отчёт для врача» — выбор периода (start_date, end_date), кнопка скачивания CSV (`GET /export/health-report`).
  - **Дашборд продуктивности**: блок на главном дашборде — вызов `GET /analytics/productivity-dashboard`, отображение best/worst weekday, трендов 14/30 дней, session_deep_work_hours_total, top_hours, focus_by_category, инсайта.
  - **Локализация**: ключи для learning (myCourses, courseTitle, kind, courseAdded/Updated, noCoursesYet), productivity (tasks, focusSessions, taskTitle, dueAt, markDone, addSession, durationMinutes, sessionType и др.), reminders (fillHealth), export (startDate, endDate), dashboard (productivityDashboard, sessionDeepWorkTotal, topHoursForFocus, focusByCategory) в en.json и ru.json.

- **Функционал по ревью (REVIEW.md 62–73): приоритет средний и низкий**
  - **Learning streak (6)**: на странице Learning вызов `GET /learning/streak`, карточка с текущей серией дней подряд и last_activity_date.
  - **Привязка задач к записи продуктивности (7)**: в EntriesPage добавлен тип поля `multiselect` (options, valueType `number[]`); на ProductivityPage поле «Выполненные задачи» (completed_task_ids) — чекбоксы по списку задач из `GET /productivity/tasks` (open/done), отправка в create/update записи продуктивности.
  - **Цели по новым метрикам (8)**: в `GOAL_METRICS_BY_SPHERE` для сферы health добавлены `steps`, `workout_minutes`; в настройках целей для health доступен выбор target_metric = steps, workout_minutes.
  - **Фоновый sync (9)**: `POST /integrations/{provider}/sync` создаёт job через `create_sync_job(..., data_source_id=source.id)` и сразу возвращает job; синхронизация выполняется в фоне через `BackgroundTasks` (`_execute_sync_background` с новой сессией БД). `run_sync` принимает опциональный `job` для обновления существующего job; на фронте можно опрашивать `GET /sync-jobs` или статус источника до завершения.
  - **PDF-экспорт (10)**: заглушка `GET /export/health-report-pdf` — возвращает 501 с сообщением «PDF export not implemented; use CSV».
  - **Календарь занятий Learning (11)**: на странице Learning блок «Learning by date» — таблица по дням (дата, часы учёбы, количество записей) за последние 14 дней на основе списка записей.
  - **Pomodoro-таймер (12)**: на странице Productivity виджет «Pomodoro timer» — обратный отсчёт (25 мин по умолчанию), кнопки «Start», «Pause», «Finish session»; по «Finish session» отправка `POST /productivity/sessions` с duration_minutes и session_type pomodoro.
  - **Локализация**: ключи learning (lastActivity, byDate, byDateHint, entriesCount), productivity (completedTasks, pomodoroTimer, pomodoroTimerHint, startTimer, pauseTimer, finishSession) в en.json и ru.json.

- **Улучшения по ревью (REVIEW.md 76–84): код и архитектура backend**
  - **Валидация**: для `source_type`, `focus_category`, `session_type` в Pydantic-схемах используются `Literal` (LearningSourceType, FocusCategoryType, SessionType); `entry_type` — уже с Literal (day/morning/evening).
  - **Конфиг**: константы `GOOGLE_OAUTH_AUTH_URL`, `GOOGLE_OAUTH_TOKEN_URL`, `FITNESS_AGGREGATE_URL`, `MAX_IMPORT_FILE_SIZE_BYTES` вынесены в `backend/app/core/config.py` (Settings), чтение из env с дефолтами.
  - **Разделение слоёв**: маппинг Fitness API → HealthEntry вынесен в `map_fitness_steps_to_health_entries()` в `backend/app/integrations/google_fit.py`; маппинг Apple XML → HealthEntry — в отдельную функцию `map_apple_health_to_health_entries()` в `backend/app/integrations/apple_health.py`; routes остаются тонкими.
  - **Ошибки в интеграциях**: при падении fetch в sync логируется traceback (`logging.exception`), усечённое сообщение сохраняется в `last_error` источника.
  - **Rate limit**: общий rate limit по IP через slowapi (Limiter с default_limits, SlowAPIMiddleware); лимит настраивается через `RATE_LIMIT_DEFAULT` (по умолчанию 200/minute).

- **Улучшения по ревью (REVIEW.md 87–91): код и UX frontend**
  - **Типы**: синхронизация типов в `entries.ts`, `integrations.ts`, `analytics.ts`, `goals.ts` с актуальными API-ответами (новые поля и вложенные объекты).
  - **Обработка ошибок**: единообразная обработка 4xx/5xx через axios interceptor (client.ts): 401 → редирект на логин и API_ERROR_EVENT; остальные ошибки (кроме 422) → API_ERROR_EVENT для вывода в тост/баннер.
  - **Загрузка состояний**: скелетоны при `isLoading` на Dashboard (пока загружаются health/finance/productivity/learning), Goals, Integrations, EntriesPage, WeeklyReportPage.
  - **Доступность (a11y)**: aria-label у кнопок (дашборд, цели, интеграции и др.), role="status" у баннеров; при необходимости — роли и подписи к графикам.

- **Улучшения по ревью (REVIEW.md 95–97): CI и pre-commit**
  - **CI**: прогон миграций (`alembic upgrade head`) на SQLite перед тестами; smoke-тесты основных эндпоинтов — health, goals, analytics (GET с авторизацией).
  - **Pre-commit**: ruff (check + format) по backend/ и корневым Python-файлам; линтер фронта (ESLint) по `frontend-react/` при изменении файлов в этой директории.

- **Расширение функционала (REVIEW.md 100–103, 107–108) — реализовано**
  - **Виджеты дашборда**: кнопка «Настроить дашборд» на дашборде; чекбоксы для включения/выключения блоков (цели, экспорт, тренды, графики, корреляции, инсайты и др.); сохранение в профиле (PATCH /auth/me, dashboard_settings.enabled_blocks) и fallback в localStorage.
  - **Уведомления**: в профиле (Настройки) — поле «Email для напоминаний» и чекбокс «Отправлять напоминания по email»; бэкенд: поля User.notification_email, User.notification_preferences; скрипт `python -m backend.app.tasks.reminder_emails` (SMTP: SMTP_HOST, SMTP_USER, SMTP_PASSWORD и др.) для отправки напоминаний «здоровье за вчера» и «не заполнял N дней»; запуск по cron или воркеру.
  - **Цели «закончить курс»**: target_metric = course_complete, привязка к course_id (обязателен при создании цели); LearningCourse.completed_at для ручной отметки «завершён»; прогресс цели = 100% при completed_at, иначе 0%; на странице Learning — кнопки «Отметить завершённым» / «Снять отметку» у курса; в Настройках при добавлении цели по сфере learning — метрика «Закончить курс» и выбор курса.
  - **Категории расходов**: таблица user_expense_category_mappings (user_id, provider_category, target_field); API GET/POST/PATCH/DELETE /finance/category-mappings; на странице Финансы — секция «Маппинг категорий расходов» (список маппингов, добавление: категория провайдера → поле учёта); в open_banking при синке используется маппинг пользователя вместо дефолтного CATEGORY_MAP.
  - Миграция `0011_dashboard_notif_goals_expense`: users (dashboard_settings, notification_email, notification_preferences), user_goals (course_id), learning_courses (completed_at), user_expense_category_mappings.
