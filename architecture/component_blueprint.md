# Component blueprint — MVP Поток 1 (AS-IS + TO-BE)

## Основание / Scope
Основание: `official_requirements_specification.md`, `technical_assignment_tz.md`, `uat_acceptance_scenarios.md`,
`calculator_formula_specification.md`, `knowledge_base_corpus_register.md`, `decision_log.md`,
`dialog_auto_selection_analysis.md`.

Scope: только **Поток 1 (Telegram-консультант)**. Поток 2 (логистика) — out-of-scope для MVP и запускается только
после заполнения `logistics_api_matrix.md`.

Реализация (AS-IS): FastAPI-сервис `services/consultant_api` + PostgreSQL (см. `docker-compose.yml`).

## AS-IS (реализовано)

### Компоненты (границы и ответственности)
1) **Telegram ingress (Webhook controller)**
   - Endpoint: `POST /telegram/webhook`.
   - Проверка `X-Telegram-Bot-Api-Secret-Token` (если включен `TELEGRAM_WEBHOOK_SECRET_TOKEN`).
   - Пишет `audit_events` (тип `telegram.update`) и входящее сообщение в `messages`.

2) **Dialog engine**
   - Логика вопросов/нормализации: `app/services/dialog_engine.py`.
   - Состояние диалога хранится в `conversations` (`state`, `data`, `bot_paused`).
   - Сейчас собирается фиксированный набор полей (15 полей), после чего диалог помечается как `qualified`.

3) **Escalation / Manager takeover**
   - Правило takeover: если пользователь с ролью `manager` пишет в чат — `conversations.bot_paused = true` до команды
     `/resume_bot`.
   - Эскалации создаются как записи `escalations` в случаях:
     - бюджет ниже порога (reason_code=`budget_below_threshold`);
     - любое сообщение после квалификации (reason_code=`post_qualification_message`).
   - Уведомление менеджера: через отправку сообщения в `TELEGRAM_MANAGER_CHAT_ID` (если задан).

4) **Calculator v1**
   - Реализован как библиотека: `app/services/calculator.py`.
   - Используется только в Admin endpoint `POST /admin/estimates/preview` (не интегрирован в Telegram-диалог).

5) **Knowledge base (структура + модерация)**
   - Хранилище и CRUD: `kb_sources`, `kb_docs` через Admin API.
   - В Telegram-диалоге сейчас нет retrieval/использования KB для ответов клиенту.

6) **Admin API**
   - Минимальные endpoints (см. `app/routers/admin.py`): health, fx_rates, rates, estimate preview, kb, users/roles,
     экспорт лидов.
   - Аутентификация: `X-Admin-Token` только если задан `ADMIN_API_TOKEN` (в dev может быть пустым).

7) **Audit logging**
   - Таблица `audit_events` фиксирует технические и бизнес-события (например: `telegram.update`, `bot.pause`,
     `bot.resume`, `lead.qualified`, `escalation.created`).

8) **PostgreSQL**
   - Основное хранилище доменных сущностей и аудита.

### Доменные сущности (модель данных, AS-IS)
Ссылка на реализацию: `services/consultant_api/app/models.py`.

- `roles` (`Role`): роль пользователя (например `manager`).
- `users` (`User`): Telegram user_id + роль.
- `conversations` (`Conversation`): чат, состояние и собранные данные.
- `messages` (`Message`): вход/выход сообщения (в коде сейчас пишется только `direction="in"`).
- `leads` (`Lead`): зафиксированные обращения (создается при квалификации и при low budget).
- `escalations` (`Escalation`): причины передачи менеджеру (создается в двух сценариях).
- `audit_events` (`AuditEvent`): событийный журнал.
- `kb_sources` / `kb_docs`: база знаний (источники и документы).
- `fx_rates`: курсы валют (CBR).
- `rate_items`: статьи/ставки (справочник).
- `settings`: key/value (например overrides курсов).
- `estimates` (`Estimate`): модель есть в коде, но на данный момент не используется в роутерах → GAP.

### Основные потоки (под UAT) — AS-IS vs ожидаемое

#### BOT-UAT-01 “Первичная квалификация”
AS-IS:
1) Клиент пишет в чат → `POST /telegram/webhook`.
2) Создается `Conversation` при первом сообщении.
3) Сообщения пишутся в `messages`, диалог задает вопросы по списку полей.
4) После заполнения всех полей: `Conversation.state="qualified"`, создается `Lead(status="qualified")`,
   отправляется уведомление менеджеру (если задан канал).

Ожидаемое (UAT): “бот собирает 15 параметров или корректно уточняет недостающие” — в целом совпадает.

#### BOT-UAT-02 “Бюджет ниже 1 500 000”
AS-IS:
- При вводе `budget_rub < 1_500_000` создается `Escalation(budget_below_threshold)` и `Lead(status="budget_low")`,
  бот отправляет сообщение пользователю и уведомляет менеджера.

#### BOT-UAT-08 “Подключение менеджера / takeover”
AS-IS:
- Если пишет менеджер → бот ставит `bot_paused=true` и прекращает автоответы; `/resume_bot` снимает паузу.

#### BOT-UAT-09 “Журналирование”
AS-IS:
- Есть записи `audit_events` для ключевых событий диалога и takeover, но нет явных событий расчета/KB-ответа,
  так как эти функции не подключены к Telegram-диалогу.

#### CALC-UAT-* (калькулятор)
AS-IS:
- В Telegram-диалоге нет выдачи сметы; расчет доступен только через `POST /admin/estimates/preview`.

## TO-BE (target MVP)

### Компоненты (минимальный target для прохождения UAT baseline)
1) **Telegram ingress** — быстрый прием update + минимальная валидация + постановка обработки в очередь/фон (если нужно
   для быстрого ответа).
2) **Dialog engine** — квалификация + ветвления по правилам (budget/страна/контур калькулятора).
3) **Escalation engine** — единая таксономия причин эскалации + передача контекста менеджеру.
4) **Calculator service v1** — формирование сметы “под ключ” в рамках v1 + хранение версии формулы, источника FX,
   timestamp и использованных ставок.
5) **KB retrieval** — ответы только из `approved` источников; при низкой уверенности/конфликте → эскалация.
6) **Admin API** — управление ставками/FX/KB/пользователями + (опционально) управление pause/resume бота через админку.
7) **Audit & metrics** — событийный аудит + минимальные метрики эксплуатации.

### Профиль данных TO-BE (минимум)
- `Estimate` становится “offer snapshot”: хранит items, total, formula_version, fx_source/timestamp, fx_rates,
  связанные `conversation_id` и ссылку на исходные параметры.

## Gaps
- UAT BOT-UAT-03/04/05/06/07 и CALC-UAT-* требуют поведения (смета, KB-ответы, shortlist, эскалации вне контура),
  которое не реализовано в Telegram-диалоге.
- `Estimate` определен в модели, но не создается и не используется в API/Telegram контуре.
- Нет идемпотентности webhook и защиты от дублей (update_id/message_id) — возможны повторные записи и повторная логика.
- `send_message()` выполняется синхронно с таймаутом 15s — риск превышения ожиданий Telegram webhook и дублей.
- RBAC как модель данных существует, но реально ограничение прав на уровне endpoints отсутствует (кроме admin token).

## Открытые вопросы
- SLA ответа менеджера после эскалации (см. вопрос в `dialog_auto_selection_analysis.md`).
- Нужна ли фиксация/“заморозка” курса на срок оффера (влияние на модель `Estimate` и UX).
- Требуется ли административное управление takeover (pause/resume) помимо команды `/resume_bot`.
