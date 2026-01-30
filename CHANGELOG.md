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
  - Категория фокуса: поле `focus_category` в записях продуктивности (code / writing / meetings / other) для аналитики «на что уходит время».
  - Сессии фокуса (Pomodoro/таймеры): таблица `focus_sessions`, `POST /productivity/sessions`, `GET /productivity/sessions` (duration_minutes, session_type: pomodoro/deep_work); агрегация по дате для отчётов.

- **Напоминания**
  - API напоминаний: `GET /reminders` — список напоминаний (тип, should_remind, message); напоминание «заполни здоровье за вчера» при отсутствии записи за вчера.

- **Миграция**
  - `0007_health_learning_productivity_extensions`: health (entry_type, steps, heart_rate_avg, workout_minutes), learning_courses + course_id/source_type в learning_entries, productivity_tasks + focus_category в productivity_entries, focus_sessions.

- **Интеграции и биллинг (заготовки)**
  - Интеграции: список провайдеров, подключение, синхронизация (Google Fit, Apple Health, Open Banking); модели источников и заданий синхронизации, хранение токенов; баннер «OAuth coming soon».
  - Биллинг: модели планов и подписок, эндпоинты subscribe/subscription, страница Billing; пометка «Billing is in demo mode. No real charges.»; в README — что оплата пока не подключена.

- **Ревью продукта (лендинг и UX)**
  - Лендинг: hero на выгоды и ЦА; блок про бесплатный аккаунт и премиум «coming soon»; социальное доказательство.
  - При залогиненном пользователе `/` перенаправляет на `/dashboard`.
  - index.html: meta description и Open Graph.
  - README: развёртывание одной командой (миграции при старте backend), Backlog (Forgot password, подключение оплаты).
