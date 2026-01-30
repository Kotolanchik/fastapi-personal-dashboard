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
  - README: развёртывание одной командой (миграции при старте backend), Backlog (Forgot password, подключение оплаты).
