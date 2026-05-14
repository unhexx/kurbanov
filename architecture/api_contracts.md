# API contracts — MVP Поток 1 (AS-IS + TO-BE)

## Основание / Scope
Источник: `official_requirements_specification.md`, `technical_assignment_tz.md`, `calculator_formula_specification.md`,
`knowledge_base_corpus_register.md`, `uat_acceptance_scenarios.md`.

Scope: только **Поток 1**. Поток 2 (логистика) описывается отдельно после заполнения `logistics_api_matrix.md`.

Реализация (AS-IS): `services/consultant_api/app/routers/telegram.py`, `services/consultant_api/app/routers/admin.py`.

## AS-IS (реализовано)

### Общие соглашения
- Формат данных: JSON, `Content-Type: application/json` (кроме CSV-экспорта).
- Формат времени: ISO8601 + `Z` (UTC) в ответах (см. `/admin/health`, `/admin/fx_rates`).
- Ошибки: FastAPI формат `{ "detail": <string|object> }`.
  - В части сценариев `detail` — стабильный код (например `scope_*` из калькулятора).
  - В части сценариев `detail` — человекочитаемое сообщение (например “Unauthorized”).

### Telegram ingress
#### `POST /telegram/webhook`
Auth:
- Если `TELEGRAM_WEBHOOK_SECRET_TOKEN` задан, требуется header `X-Telegram-Bot-Api-Secret-Token` со значением токена.
- При неверном/отсутствующем токене: `401` `{ "detail": "Unauthorized" }`.

Request body:
- `update: object` — “сырой” Telegram Update (обрабатываются только `message` и `edited_message`).

Behavior (high level):
1) Записывает `audit_events(event_type="telegram.update")` с `payload=update`.
2) Если в update нет `message`/`edited_message` → возвращает `{ "ok": true }` без дальнейших действий.
3) Иначе:
   - создает/находит `Conversation` по `chat_id`;
   - пишет входящее сообщение в `messages(direction="in", raw=<message>)`;
   - применяет правила takeover / паузы бота / квалификации / эскалаций.

Special cases:
- Takeover менеджером:
  - если отправитель сопоставлен `users.telegram_user_id` и его `roles.code == "manager"`, то:
    - при тексте `/resume_bot` → `conversations.bot_paused=false`, audit `bot.resume`, бот отправляет “Бот снова активен.”
    - иначе → `conversations.bot_paused=true`, audit `bot.pause`, без автоответа клиенту
- Если `conversations.bot_paused=true` и пишет клиент → `{ "ok": true }` без обработки.
- Если `conversations.state=="qualified"` и пишет клиент → создается `Escalation(reason_code="post_qualification_message")`
  и audit `escalation.created`, клиенту отправляется “Передаю уточнение менеджеру.”, менеджеру уходит summary.

Responses:
- `200` `{ "ok": true }` (всегда при успешной обработке).

Errors:
- `401` Unauthorized (только при включенном secret token).

### Admin API
Все endpoints требуют `X-Admin-Token` **только если** задан `ADMIN_API_TOKEN`.
Если `ADMIN_API_TOKEN` пустой — endpoints доступны без токена (dev режим).

#### `GET /admin/health`
Response `200`:
```json
{"ok": true, "time": "2026-05-14T10:15:30.123Z"}
```

#### `POST /admin/fx_rates/refresh`
Behavior:
- Загружает XML CBR по `CBR_DAILY_URL` (по умолчанию `https://www.cbr.ru/scripts/XML_daily.asp`).
- Парсит и upsert’ит `fx_rates`.
Response `200`:
```json
{"rate_date": "2026-05-14", "upserted": 35}
```
Errors:
- `5xx` при сетевых/парсинговых ошибках (через исключения/raise_for_status()).

#### `GET /admin/fx_rates?rate_date=YYYY-MM-DD`
Response `200`: массив объектов:
- `rate_date: string`
- `char_code: string`
- `nominal: int`
- `rate_rub: string`
- `source: string`
- `fetched_at: string (ISO8601Z)`

#### `POST /admin/fx_rates/override`
Request:
- `char_code: string` (required)
- `rate_rub: string` (required, число как строка)
Response `200`: `{ "ok": true, "char_code": "USD", "rate_rub": "90.0" }`
Errors:
- `400` если отсутствуют `char_code` или `rate_rub`.

#### `GET /admin/fx_rates/overrides`
Response `200`: массив объектов `{ "char_code": "USD", "rate_rub": "90.0" }`

#### `POST /admin/rates`
Request:
- `code: string` (required)
- `title: string` (required)
- `currency: string` (optional, default `"RUB"`)
- `amount: number|null` (optional)
- `min_amount: number|null` (optional)
- `max_amount: number|null` (optional)
Response `200`: `{ "ok": true, "code": "<code>" }`
Errors:
- `400` если отсутствуют `code` или `title`.

#### `GET /admin/rates`
Response `200`: массив объектов:
- `code: string`
- `title: string`
- `currency: string`
- `amount: string|null`
- `min_amount: string|null`
- `max_amount: string|null`

#### `POST /admin/estimates/preview`
Назначение: “предпросмотр” расчета (без сохранения).

Request:
- `country: string`
- `age_years: int`
- `power_hp: int`
- `car_price_rub: string|number`
- `export_cost_rub: string|number`
- `commission_rub: string|number`
- `broker_rub: string|number`
- `logistics_rub: string|number`
- `customs_rub: string|number`
- `extra_costs_rub: string|number`
Response `200`:
```json
{
  "formula_version": "v1.0",
  "total_rub": "1645000.00",
  "items": [{"code":"car_price","title":"Цена автомобиля","amount_rub":"1000000"}]
}
```
Errors:
- `400` `{ "detail": "scope_country_out_of_v1" | "scope_age_out_of_v1" | "scope_power_out_of_v1" }`

#### `GET /admin/leads/export.csv`
Response `200`:
- `Content-Type: text/csv; charset=utf-8`
- CSV header: `id,created_at,chat_id,customer_telegram_user_id,status,payload`

#### `POST /admin/kb_sources`
Request:
- `code: string` (required)
- `title: string` (required)
- `url: string|null`
- `format: string|null`
- `owner: string|null`
- `moderation_status: string|null` (optional; если не передан — остается текущий)
- `notes: string|null`
Response `200`: `{ "ok": true, "code": "<code>" }`
Errors:
- `400` если отсутствуют `code` или `title`.

#### `GET /admin/kb_sources`
Response `200`: массив объектов:
- `code`, `title`, `url`, `format`, `owner`, `moderation_status`, `updated_at`

#### `POST /admin/kb_docs`
Request:
- `source_code: string` (required)
- `title: string` (required)
- `content: string` (required)
- `tags: array` (optional, default `[]`)
- `moderation_status: string` (optional, default `"draft"`)
Response `200`: `{ "ok": true, "id": "<uuid>" }`
Errors:
- `400` если отсутствуют `source_code`/`title`/`content`
- `404` если `kb source not found`

#### `GET /admin/kb_docs?source_code=...`
Response `200`: массив объектов `{ id, source_code, title, moderation_status, updated_at }`

#### `POST /admin/roles`
Request: `code` (required), `title` (required)
Response `200`: `{ "ok": true, "code": "<code>" }`
Errors: `400` если отсутствуют `code`/`title`.

#### `GET /admin/roles`
Response `200`: массив `{ code, title }`

#### `POST /admin/users`
Request:
- `telegram_user_id: int` (required)
- `role_code: string` (required)
- `username: string|null`
- `is_active: bool` (optional, default `true`)
Response `200`: `{ "ok": true, "telegram_user_id": 123 }`
Errors:
- `400` если отсутствуют `telegram_user_id`/`role_code`
- `404` если `role not found`

#### `GET /admin/users`
Response `200`: массив объектов `{ id, username, telegram_user_id, role_code, is_active }`

## TO-BE (target MVP)
Минимальные контрактные дополнения для прохождения UAT baseline (как спецификация к реализации; не считать “реализованным”):

1) **Calculator in Telegram flow**
   - Возможность сформировать смету “под ключ” в контуре v1 из диалога или по команде менеджера.
   - Смета должна содержать: `formula_version`, `fx_source`, `fx_timestamp`, `items[]`, `total`.
   - Смета должна быть сохранена как `Estimate` (offer snapshot) и быть воспроизводимой (immutability).

2) **KB answers policy**
   - Ответы пользователю по комплектациям/правилам — только из источников со статусом `approved`.
   - При отсутствии/конфликте/низкой уверенности — эскалация менеджеру с передачей контекста и ссылок на источники.

3) **Idempotency / duplicates**
   - В webhook обработчике нужна защита от дублей (повторной доставки update) как минимум по `update.update_id`
     и/или `message.message_id` + `chat_id`.
   - Политика: повторный update не должен повторно создавать `Lead`/`Escalation` и не должен повторно отправлять
     сообщения клиенту.

4) **Admin control for takeover (optional)**
   - Endpoint для `pause/resume` бота на уровне `Conversation`, чтобы не зависеть только от `/resume_bot`.

## Gaps
- В Telegram контуре отсутствуют CALC-UAT-* и ответы по KB/shortlist (BOT-UAT-03/05/06/07) — требуется реализация.
- Нет гарантированной идемпотентности webhook; при ретраях возможны дубли записей и повторные side-effects.
- `send_message()` синхронный и без обработки ошибок Telegram API — риск таймаутов и “молчаливых” потерь уведомлений.

## Открытые вопросы
- Требуется ли “заморозка” курса/ставок на срок оффера (влияет на контракт `Estimate`).
- SLA ответа менеджера после эскалации (и нужна ли автоматическая повторная эскалация/напоминание).
