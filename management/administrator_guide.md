# Инструкция администратора сервиса

Документ описывает запуск, проверку версии, настройку окружения и эксплуатационные действия.
Актуальная версия приложения FastAPI - `0.1.0`, версия расчетной формулы - `v1.0`.

## Локальный smoke-запуск

Основной способ проверки в текущем WSL-окружении - SQLite smoke-режим. Docker CLI может быть
недоступен без Docker Desktop WSL integration.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r services/consultant_api/requirements-dev.txt

rm -f /tmp/kurbanov_smoke.db
export DATABASE_URL=sqlite+pysqlite:////tmp/kurbanov_smoke.db
export ADMIN_API_TOKEN=
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/init_db.py
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/seed.py

python3 -m uvicorn app.main:app --app-dir services/consultant_api --host 127.0.0.1 --port 18000
```

Проверочные адреса:

- `http://127.0.0.1:18000/` - публичный портал;
- `http://127.0.0.1:18000/intake` - анкета;
- `http://127.0.0.1:18000/calculator` - публичный калькулятор;
- `http://127.0.0.1:18000/admin` - админка;
- `http://127.0.0.1:18000/docs` - Swagger UI;
- `http://127.0.0.1:18000/admin/health` - health-check.

## Проверка версии

Версия приложения берется из OpenAPI:

```bash
curl -fsS http://127.0.0.1:18000/openapi.json
```

В ответе должно быть:

```json
{"info": {"version": "0.1.0"}}
```

Версия расчетной формулы проверяется через калькулятор или admin API:

```bash
curl -fsS -X POST http://127.0.0.1:18000/admin/estimates/preview \
  -H 'Content-Type: application/json' \
  -d '{"country":"РФ","age_years":4,"power_hp":150,"car_price_rub":"1000000","export_cost_rub":"10000","commission_rub":"50000","broker_rub":"85000","logistics_rub":"200000","customs_rub":"300000","extra_costs_rub":"0"}'
```

В ответе должно быть поле `"formula_version": "v1.0"`.

## Переменные окружения

Обязательные и основные параметры:

- `DATABASE_URL` - строка подключения к PostgreSQL или SQLite;
- `ADMIN_API_TOKEN` - токен входа в web-админку и защиты admin API;
- `TELEGRAM_BOT_TOKEN` - токен Telegram-бота;
- `TELEGRAM_WEBHOOK_SECRET_TOKEN` - секрет webhook, если используется защита входящих
  запросов от Telegram;
- `TELEGRAM_MANAGER_CHAT_ID` - чат для уведомлений менеджеру;
- `PERPLEXITY_API_KEY` - ключ внешнего сервиса ответов консультанта;
- `FORMULA_VERSION` - версия расчетной формулы, по умолчанию `v1.0`;
- `BUDGET_THRESHOLD_RUB` - бюджетный порог передачи менеджеру;
- `CONSULTANT_HISTORY_LIMIT` - размер истории диалога для консультанта.

Секреты должны храниться только в локальном `.env` или в секретах окружения. Не коммитьте
реальные токены и API-ключи.

## Администрирование данных

- `/admin/rates` - добавление и изменение ставок и сборов.
- `/admin/fx` - обновление курсов из ЦБ и ручные переопределения валют.
- `/admin/kb` - источники базы знаний и добавление документов.
- `/admin/users` - роли и Telegram-пользователи для takeover менеджером.
- `/admin/leads` - просмотр и CSV-экспорт лидов.

Базовые роли и источники базы знаний создаются командой:

```bash
PYTHONPATH=services/consultant_api python3 services/consultant_api/scripts/seed.py
```

## Health-check и диагностика

Проверка доступности admin API:

```bash
curl -fsS http://127.0.0.1:18000/admin/health
```

Ожидаемый ответ содержит `{"ok": true}` и UTC-время. Если задан `ADMIN_API_TOKEN`, для JSON
admin API передавайте заголовок `X-Admin-Token`.

## Здоровье AI-контура (Perplexity / генерация ответов консультанта)

Когда используется внешний сервис генерации ответов, за его состоянием нужно следить отдельно.

**Признаки проблем с AI-контуром:**

- Резкий рост эскалаций с `reason_code = "low_confidence"` (особенно за последние 10–30 минут).
- Появление `AuditEvent` с `event_type = "consultant.api_error"`.
- Клиенты жалуются, что бот «перестал отвечать по делу» или сразу передаёт менеджеру.

**Где смотреть:**

- Дашборд админки — счётчик «Эскалаций».
- Таблица `escalations` (поле `reason_code` и `details`).
- Таблица `audit_events` (фильтр по `consultant.api_error` и `escalation.created`).
- Логи приложения (если настроен structured logging) — там фиксируются таймауты, статусы ответов и ошибки парсинга.

**Что происходит при сбоях:**

При отсутствии ключа (`PERPLEXITY_API_KEY` пустой или невалидный) или при ошибках сервиса консультант автоматически переходит в rule-based режим: просто задаёт следующий вопрос анкеты дословно, без попытки «умных» ответов. Сервис при этом не падает.

Если сбои продолжаются долго — рекомендуется временно отключить ключ или перевести весь трафик в rule-based до восстановления внешнего сервиса.

## Тесты

После установки зависимостей запустите:

```bash
cd services/consultant_api
python3 -m pytest -s -q tests
```

Флаг `-s` используется в текущем окружении, чтобы избежать проблем pytest capture во WSL.

## Безопасность

- На shared, stage и production окружениях `ADMIN_API_TOKEN` должен быть непустым.
- `TELEGRAM_WEBHOOK_SECRET_TOKEN` включайте для публичного webhook.
- `PERPLEXITY_API_KEY`, Telegram-токены и admin-токены не должны попадать в Git.
- После проверки локального smoke-запуска не используйте SQLite-базу из `/tmp` как
  долговременное хранилище.
