# NFR checklist — MVP Поток 1 (AS-IS + TO-BE)

## Основание / Scope
Основание: `official_requirements_specification.md`, `technical_assignment_tz.md`, `uat_acceptance_scenarios.md`,
`pre_kp_customer_questionnaire_and_input_data.md`, текущая реализация `services/consultant_api`.

Scope: Поток 1 (Telegram-консультант). Поток 2 (логистика) — отдельно.

## AS-IS (реализовано)

### Надежность
- [x] Все ключевые артефакты пишутся в PostgreSQL (диалоги/сообщения/лиды/аудит).
- [x] Идемпотентность webhook (защита от дублей update/message) реализована:
      дедупликация по `update_id` (fallback: `chat_id + message_id`) с персистентным хранением.
- [ ] Ошибки Telegram API не обрабатываются: `send_message()` не проверяет статус/исключения и выполняется синхронно.
- [x] Таймауты внешних запросов выставлены на 15s (Telegram/CBR), но без retry/backoff.

### Безопасность
- [x] Поддержка проверки `TELEGRAM_WEBHOOK_SECRET_TOKEN` через header `X-Telegram-Bot-Api-Secret-Token`.
- [x] Admin API может быть защищен `ADMIN_API_TOKEN`, но в dev допускается пустой токен (endpoint’ы открыты).
- [ ] RBAC не enforced на уровне API: модель ролей есть, но доступы к admin endpoints завязаны только на токен.
- [ ] Политика хранения/удаления персональных данных (PII retention) не зафиксирована.

### Наблюдаемость
- [x] Есть событийный журнал `audit_events` (telegram.update, lead.qualified, escalation.created, bot.pause/resume).
- [ ] Нет метрик/трейсов/корреляции запросов (request_id), только audit_events.
- [ ] Нет алертов на провалы доставки уведомлений менеджеру/ошибки Telegram API.

### Производительность
- [x] Target нагрузки для первой версии: до 10 одновременных диалогов (baseline из опросника).
- [ ] Webhook handler делает “тяжелую” работу синхронно (включая сетевые вызовы Telegram API на отправку сообщений).
      Это повышает риск таймаутов и повторной доставки update.

## TO-BE (target MVP)

### Надежность
- [ ] Webhook idempotency:
  - Дедупликация по `update_id` (и/или `chat_id + message_id`) с TTL или персистентным хранением.
  - Повторная доставка не должна порождать повторные side-effects (дубли лидов/эскалаций/сообщений).
- [ ] Telegram API resiliency:
  - Отправка сообщений с retry/backoff на 5xx/сетевые ошибки.
  - Явное логирование/аудит ошибок доставки (с `event_type=telegram.send_failed`).
- [ ] DB backups (baseline):
  - Ежедневный бэкап PostgreSQL.
  - RPO ≤ 24h, RTO ≤ 8h (baseline для MVP, уточняется в `decision_log.md` при необходимости).
- [ ] Транзакционность (baseline):
  - Для webhook: атомарность записи “входящее сообщение + состояние диалога + audit” (либо единая транзакция, либо
    компенсирующая логика).

### Безопасность
- [ ] Enforce секреты в non-dev:
  - `TELEGRAM_WEBHOOK_SECRET_TOKEN` обязателен в shared/stage/prod.
  - `ADMIN_API_TOKEN` обязателен в shared/stage/prod.
- [ ] RBAC baseline:
  - Роли существуют (admin/manager/content_operator/observer) и проверяются на уровне API для админки.
  - Минимум: “observer” read-only, “content_operator” только KB, “admin” все.
- [ ] Secret management:
  - Токены и ключи только через env/secret store (не в коде/репозитории).
- [ ] PII retention:
  - Определить сроки хранения сообщений/лидов и процедуру удаления по запросу (baseline policy).

### Наблюдаемость
- [ ] Audit baseline (BOT-UAT-09):
  - Обязательные события: диалог (старт/шаг/квалификация), эскалация (создание/закрытие), расчет (создание сметы),
    действия менеджера (pause/resume), ошибки интеграций (Telegram/CBR).
- [ ] Корреляция:
  - В каждый audit_event добавлять `conversation_id` и корреляционный идентификатор запроса (request_id).
- [ ] Метрики (минимум):
  - dialogs_total, escalations_total (by reason_code), leads_total (by status), webhook_errors_total,
    telegram_send_fail_total, calc_out_of_scope_total.
- [ ] Логи:
  - Структурированные логи уровня INFO/WARN/ERROR для входящих update и внешних вызовов.

### Производительность
- [ ] Webhook latency baseline:
  - P95 время ответа webhook ≤ 1s (рекомендовано), тяжелую обработку переносить в фон при необходимости.
- [ ] Таймауты:
  - Внешние запросы (Telegram, CBR) с ограничениями по времени и retry policy.
- [ ] DB:
  - Пул соединений и лимиты запросов, индексы по `chat_id`, `created_at` и ключевым полям уже есть частично;
    дополнения вносить по профилированию при росте нагрузки.

## Gaps
- Нет метрик/алертов и обработки ошибок доставки сообщений; это повышает риск “тихих” сбоев.
- Без `ADMIN_API_TOKEN` окружение становится полностью открытым — требуется правило для non-dev.
- RBAC не реализован как политика доступа на endpoint’ах (есть только модель данных).

## Открытые вопросы
- Нужно ли гарантировать SLO по времени ответа менеджера (эскалация) и механизм напоминаний?
- Требуются ли юридические/комплаенс ограничения по хранению переписки и ссылок на источники?
