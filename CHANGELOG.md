# История изменений

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).  
Версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

---

## [Не выпущено]

### Добавлено

- **Интеграция LLM (AI Assistant)**
  - Backend: модуль `llm` с клиентом OpenAI-совместимого API (OpenAI, Ollama и др.); конфиг `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`.
  - API: `POST /llm/chat` — чат с ассистентом (опционально контекст из аналитики); `GET /llm/insight` — один инсайт по данным пользователя на основе сводки инсайтов.
  - Frontend: страница «AI Assistant» в навигации; чат с подстановкой контекста дашборда; кнопка «Один инсайт по данным»; тосты при ошибке (LLM не настроен).
  - Зависимость: `openai>=1.0.0`; примеры переменных окружения в `.env.example` и комментарии в `docker-compose.full.yml`.

- **Глобальная локализация (EN / RU)**
  - i18next, react-i18next, i18next-browser-languagedetector; инициализация в `src/i18n.ts`, ресурсы `src/locales/en.json` и `src/locales/ru.json`.
  - Ключи по разделам: common, nav, auth, landing, dashboard, onboarding, inactiveReminder, goals, settings, assistant, entries, reports, errors, billing, integrations, legal, layout.
  - Переключатель языка (EN | RU) в шапке Layout; сохранение выбора в `localStorage` (`lifepulse_lang`).
  - Все пользовательские строки заменены на `t()` во всех страницах и общих компонентах (Layout, Footer, Landing, Auth, Dashboard, Goals, Settings, Assistant, Entries, Reports, Billing, Integrations, Legal, Onboarding, InactiveReminder, NotFound).
  - Даты в еженедельном отчёте форматируются по текущей локали (ru-RU / en-US).

- **Ревью LifePulse (промпты по действиям)**
  - Лендинг: hero переписан на выгоды и ЦА («люди, ведущие дневники и трекеры»); заголовок и подзаголовок отвечают на «зачем» и «что получу»; добавлен блок про бесплатный аккаунт и премиум «coming soon»; блок социального доказательства («Join others who track their life data»).
  - UX: при залогиненном пользователе переход на `/` автоматически перенаправляет на `/dashboard`.
  - UI: весь интерфейс на английском (подпись «Пароль» заменена на «Password»).
  - Billing: на странице Billing явная пометка «Billing is in demo mode. No real charges.»; для планов добавлены краткие описания фич (Free/Pro); в README указано, что оплата пока не подключена.
  - index.html: meta description и Open Graph (og:title, og:description, og:type).
  - Integrations: баннер «OAuth for Google Fit / Apple Health coming soon. For now you can connect with tokens below.»
  - README: в разделе «Развёртывание одной командой» добавлена фраза про миграции при старте backend; раздел Backlog с пунктами Forgot password и подключение оплаты.
- **Напоминание о неактивности**  
  При входе на дашборд проверяется давность последней записи (по всем сферам). Если записей нет или последняя старше 3 дней — показывается модальное окно: «You haven't logged in X days. Log today?» с кнопками «Log today» (переход в форму Health) и «Later» (скрыть до конца сессии).

---

## [2.5.0]

### Добавлено

- **Аналитика и инсайты (расширение)**
  - **analytics.py**: лучший/худший день недели по сну и продуктивности (агрегация по weekday); линейный тренд за 14/30 дней по сну, расходам, глубокой работе; новые инсайты: «расходы растут быстрее дохода», «после выходных сон хуже», «фокус выше в дни с ≥6 ч сна»; `trend_this_month()`, `insight_of_the_week()`, `weekday_and_trends_payload()`.
  - **recommender.py**: правила по тренду расходов vs дохода (30 дней), сон после выходных, фокус при ≥6 ч сна.
  - **API**: `GET /analytics/trend-this-month`, `GET /analytics/insight-of-the-week`, `GET /analytics/weekday-trends`; схемы TrendThisMonthResponse, InsightOfTheWeekResponse, WeekdayTrendsResponse.
  - **Дашборд**: блок «Trend this month» (↑/↓ по ключевым метрикам); «Insight of the week» поверх инсайтов; карточка «Last week in numbers» со ссылкой на еженедельный отчёт; блок «By weekday & recent trends».
  - **Еженедельный отчёт**: страница «Last week in numbers» (суммы, средние, один инсайт); явная ссылка с дашборда.

---

## [2.4.0]

### Добавлено

- **Еженедельный отчёт**
  - Backend: `GET /analytics/weekly-report` — дайджест за последние 7 дней: сводка по сферам (здоровье, финансы, продуктивность, обучение) и один инсайт.
  - Frontend: страница «Weekly report» и пункт в навигации; отображаются период, метрики по сферам и инсайт.

---

## [2.3.0]

### Добавлено

- **Рекомендации (расширение)**
  - Расширен `recommender.py`: дополнительные правила (низкий сон, регулярность обучения, фокус vs глубокая работа, доходы vs расходы), рекомендации с учётом целей пользователя.
  - Маршрут аналитики передаёт цели пользователя в recommender; ключ кэша без изменений.

---

## [2.2.0]

### Добавлено

- **Онбординг**
  - Краткий сценарий первого запуска на дашборде: модальное окно с объяснением (здоровье, финансы, продуктивность, обучение) и предложением добавить первую запись (ссылка на Health).
  - Закрытие сохраняется в `localStorage` (`lifepulse_onboarding_completed`).

---

## [2.1.0]

### Добавлено

- **Цели**
  - Backend: таблица `user_goals`, CRUD API `/goals`, расчёт прогресса (текущее значение vs цель по сфере).
  - Frontend: управление целями в Настройках (до 2 целей), блок «Goals progress» на дашборде.
  - Миграция: `0005_add_user_goals.py`.

---

## [2.0.0]

Базовая версия продукта (до введения нумерованного changelog).

### Добавлено

- **Ядро MVP**
  - Ручной ввод данных по четырём сферам: Здоровье, Финансы, Продуктивность, Обучение.
  - CRUD для записей (создание, список, обновление, удаление) с поддержкой даты и часового пояса.
  - Дашборды и графики временных рядов (Recharts) по каждой сфере.
  - Экспорт в CSV (дневная сводка, все данные, по категориям).

- **Аналитика**
  - Корреляции между числовыми метриками (Pandas).
  - Инсайты: сон vs продуктивность, сон vs энергия, финансы vs самочувствие.
  - Правила рекомендаций: сон–энергия, глубокая работа–самочувствие, траты на еду–самочувствие.
  - Опциональное кэширование в Redis для корреляций, инсайтов и рекомендаций.

- **Аутентификация и пользователи**
  - JWT (регистрация, вход, `/auth/me`).
  - Обновление профиля (имя, часовой пояс по умолчанию), смена пароля.
  - Роли `user` и `admin`; админ-эндпоинты в `/admin/*`.

- **Интеграции (заготовка)**
  - Список провайдеров, подключение, синхронизация (Google Fit, Apple Health, Open Banking).
  - Модели источников данных и заданий синхронизации, хранение токенов.

- **Биллинг (заготовка)**
  - Модели планов и подписок, эндпоинты subscribe и subscription.
  - Страница Billing в React.

- **Frontend**
  - React (Vite, TypeScript), TanStack Query, React Router.
  - Landing, Login, Register, Dashboard, страницы Health / Finance / Productivity / Learning, Integrations, Billing, Settings.
  - Layout с боковой навигацией, баннер ошибок API, тосты.
  - Юридические страницы: Privacy и Terms.

- **Backend**
  - FastAPI, SQLAlchemy, Alembic.
  - SQLite / Postgres; опционально Redis.
  - Миграции: схема приложения, роли, интеграции и биллинг, часовой пояс по умолчанию.

- **DWH и данные**
  - Схема DWH (Alembic), экспорт в Parquet, сборка DuckDB, dbt-модели (сводки по финансам и здоровью).
  - ETL и утилиты экспорта.

- **DevOps**
  - Docker Compose (dev, prod, managed Postgres/Redis), Dockerfile для backend, frontend и React.
  - Манифесты Kubernetes и Helm chart.
  - CI (pytest), workflow публикации Docker-образов.
