# MVP Telegram-консультанта и веб-портала

Репозиторий содержит MVP сервиса подбора автомобилей:

- предпроектные, коммерческие и аналитические документы в корне репозитория;
- FastAPI-приложение в `services/consultant_api`;
- управленческие и QA-артефакты в `management`;
- архитектурные материалы в `architecture`.

## Текущий статус

В MVP реализованы:

- Telegram webhook `/telegram/webhook` с идемпотентной обработкой апдейтов;
- публичный веб-портал `/` с переходами к анкете и калькулятору;
- анкета подбора `/intake`, которая создает лиды в базе;
- калькулятор итоговой стоимости `/calculator`;
- web-админка `/admin` для сводки, лидов, ставок, курсов ЦБ, базы знаний и пользователей;
- JSON API администрирования под `/admin/*`;
- Swagger UI `/docs`;
- PostgreSQL как основной runtime storage и SQLite для локальных smoke-тестов.

Ограничения калькулятора v1: оформление в РФ, возраст автомобиля 3-5 лет, мощность до
160 л.с. Значение версии формулы задается через `FORMULA_VERSION`, по умолчанию `v1.0`.

## Требования

- Python 3.12 и `pip`;
- `python3-venv` для стандартного локального виртуального окружения;
- Docker Compose опционально, если нужен запуск PostgreSQL + API в контейнерах.

В текущем WSL-окружении Docker CLI может быть недоступен без Docker Desktop WSL
integration. В этом случае используйте локальный smoke-режим с SQLite.

## Переменные окружения

Создайте `.env` по образцу:

```bash
cp .env.example .env
```

Основные переменные:

- `DATABASE_URL` - строка подключения к БД;
- `TELEGRAM_BOT_TOKEN` - токен Telegram-бота;
- `TELEGRAM_WEBHOOK_SECRET_TOKEN` - опциональная защита webhook;
- `TELEGRAM_MANAGER_CHAT_ID` - опциональные уведомления менеджеру;
- `ADMIN_API_TOKEN` - токен входа в админку и защиты admin API;
- `PERPLEXITY_API_KEY` - ключ внешнего сервиса формирования ответов консультанта;
- `PERPLEXITY_MODEL` - модель внешнего сервиса (по умолчанию `sonar-pro`);
- `PERPLEXITY_BASE_URL`, `PERPLEXITY_MAX_TOKENS`, `PERPLEXITY_TEMPERATURE`,
  `PERPLEXITY_TIMEOUT_SECONDS`, `PERPLEXITY_MAX_RETRIES` - параметры клиента;
- `BUDGET_THRESHOLD_RUB` - бюджетный порог подбора (по умолчанию `1500000`);
- `CONSULTANT_HISTORY_LIMIT` - размер истории диалога, передаваемый в модель.

Пустой `ADMIN_API_TOKEN` допустим только для локальной разработки: web-админка и admin API
будут открыты без входа. Для shared, stage и production окружений токен обязателен.
`PERPLEXITY_API_KEY` хранится только в локальном `.env` (gitignored). В репозитории -
исключительно placeholder в `.env.example`. При пустом ключе Telegram-консультант работает
в режиме rule-based: задаёт следующий недостающий вопрос анкеты без обращения к внешнему
сервису.

## Инструкции по ролям

- [Инструкция пользователя](management/user_guide.md) - публичный портал, анкета, калькулятор
  и ограничения расчета v1.
- [Инструкция оператора и менеджера](management/operator_guide.md) - обработка лидов,
  эскалации, CSV-экспорт и takeover Telegram-диалогов.
- [Инструкция администратора](management/administrator_guide.md) - запуск, проверка версий,
  переменные окружения, администрирование данных и health-check.

## Быстрый старт: локально с PostgreSQL

Поднимите PostgreSQL:

```bash
docker compose up -d db
```

Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/consultant_api/requirements.txt
```

Инициализируйте и наполните базовые справочники:

```bash
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/init_db.py
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/seed.py
```

Запустите API:

```bash
uvicorn app.main:app --app-dir services/consultant_api --reload
```

Приложение будет доступно на `http://localhost:8000`.

## Быстрый старт: Docker Compose

```bash
docker compose up -d db api
docker compose exec api python scripts/init_db.py
docker compose exec api python scripts/seed.py
```

API и веб-интерфейс будут доступны на `http://localhost:8000`.

## Smoke-запуск без Docker

Этот режим удобен для проверки веб-приложения, если PostgreSQL или Docker недоступны.

```bash
python3 -m pip install -r services/consultant_api/requirements-dev.txt
rm -f /tmp/kurbanov_smoke.db
export DATABASE_URL=sqlite+pysqlite:////tmp/kurbanov_smoke.db
export ADMIN_API_TOKEN=
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/init_db.py
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/seed.py
python3 -m uvicorn app.main:app --app-dir services/consultant_api --host 127.0.0.1 --port 18000
```

Проверяемые URL:

- `http://127.0.0.1:18000/` - публичный портал;
- `http://127.0.0.1:18000/intake` - анкета подбора;
- `http://127.0.0.1:18000/calculator` - калькулятор;
- `http://127.0.0.1:18000/admin` - web-админка;
- `http://127.0.0.1:18000/docs` - Swagger UI;
- `http://127.0.0.1:18000/admin/health` - health check admin API.

## Проверка

Из директории сервиса:

```bash
cd services/consultant_api
python3 -m pytest -s -q tests
```

Статический анализ из корня репозитория:

```bash
ruff check services/consultant_api
```

Минимальный HTTP smoke после запуска `uvicorn`:

```bash
curl -fsS http://127.0.0.1:18000/
curl -fsS http://127.0.0.1:18000/calculator
curl -fsS http://127.0.0.1:18000/admin
curl -fsS http://127.0.0.1:18000/docs
curl -fsS http://127.0.0.1:18000/admin/health
```

## Agentic Development Loop (окружение для автономной разработки)

В репозитории настроено **agentic_loop_template/** — адаптированное окружение для закрытого self-improving цикла разработки с использованием Blackbox + MiniMax 2.5 (или аналогичных моделей).

**Основные файлы:**
- `agentic_loop_template/setup_kurbanov.ps1` — основной скрипт подготовки окружения под структуру проекта (зависимости из `services/consultant_api/`, поддержка `-Smoke` для SQLite без Docker).
- `agentic_loop_template/SYSTEM_PROMPT.md` — системный промпт с заполненными плейсхолдерами под kurbanov.
- `TASK_SPECIFICATION.md`, `PROJECT_CONTEXT.md`, `SPRINTPLAN.md` — текущий контекст и план для агента.

**Быстрый старт окружения (PowerShell):**
```powershell
cd X:\LocalRepo\kurbanov
powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1
# или для быстрого smoke-режима без PostgreSQL:
powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1 -Smoke
```

После запуска:
- Активируй: `. .\.venv\Scripts\Activate.ps1`
- Установи PYTHONPATH: `$env:PYTHONPATH = 'services\consultant_api'`

**Для Blackbox / MiniMax 2.5:**
1. Запусти `.\agentic_loop_template\Agent-Init.ps1` (он подготовит окружение и сгенерирует стартовый промпт).
2. Добавь в Custom Instructions Blackbox правила из `agentic_loop_template/Agent-Init.md`.
3. Отправь содержимое `agentic_loop_template/SYSTEM_PROMPT.md` как системный промпт.

**Важные правила цикла:**
- Все git-коммиты — только на естественном русском, голос реального разработчика (Евгений Чистяков).
- Запрещено упоминать AI/LLM/агент/MiniMax/Grok в коммитах и комментариях к коду.
- Orchestrator всегда начинает цикл с вызова `setup_kurbanov.ps1`.
- Детали — в `agentic_loop_template/AGENTIC_LOOP_README.md` и `SYSTEM_PROMPT.md`.

Это позволяет вести разработку (в т.ч. доработки Telegram-консультанта и Perplexity-интеграции) в полностью автономном режиме с самосовершенствованием.

## Структура сервиса

- `app/main.py` - сборка FastAPI-приложения;
- `app/routers/telegram.py` - Telegram webhook и логика диалога;
- `app/routers/admin.py` - JSON admin API;
- `app/web/router.py` - HTML-страницы публичной части и админки;
- `app/services/calculator.py` - расчет итоговой стоимости;
- `app/services/fx_rates.py` - загрузка и парсинг курсов ЦБ;
- `app/models.py` - SQLAlchemy-модели;
- `scripts/init_db.py` - создание таблиц;
- `scripts/seed.py` - базовые роли и источники базы знаний;
- `tests/` - unit и integration-тесты.

## Telegram-консультант

Поведение бота-консультанта `Автоподбор - Exception.Expert` описано в:

- `architecture/ai_consultant_instructions.md` - persona, матрица эскалаций, правила
  grounded-ответов, правила контекста диалога;
- `management/telegram_ai_consultant_skill.md` - операционные правила, фирменные фразы,
  чек-лист UAT.

Бот не раскрывает клиенту техническую природу и не упоминает внутренние сервисы.
Передача профильному менеджеру выполняется автоматически в сценариях: бюджет ниже
порога, прямая просьба клиента, нестандартный контур (электро, мощность > 160 л.с.,
страна вне РФ/РБ/КЗ), сообщения после квалификации, нетекстовые сообщения, низкая
уверенность модели или сбой внешнего сервиса.
