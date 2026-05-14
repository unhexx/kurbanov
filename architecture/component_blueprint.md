# Component blueprint — MVP Поток 1

Основание: `official_requirements_specification.md`, `technical_assignment_tz.md`, `decision_log.md`.

## Компоненты
1) **Telegram ingress**
   - Webhook endpoint принимает updates, валидирует secret token, пишет `audit_events`.
2) **Dialog engine**
   - Сбор параметров клиента (минимум MVP), состояние диалога хранится в `conversations.data`.
3) **Escalation / Manager takeover**
   - Правило: при исходящем сообщении менеджера бот отключается; возврат — `/resume_bot`.
   - Эскалации фиксируются в `escalations` и уведомляются менеджеру (если задан канал).
4) **Calculator v1**
   - Контур v1: РФ, 3–5 лет, до 160 л.с. (`calculator_formula_specification.md`).
   - Версионирование сметы: версия формулы, источник курсов, timestamp.
5) **Knowledge base (структура + модерация)**
   - Источники и документы с модерацией статусов (`draft/approved/restricted/deprecated`).
6) **Admin API**
   - Управление курсами/ставками/контентом/пользователями/ролями.
7) **Audit logging**
   - События диалога, расчетов, эскалаций и действий менеджера.

## Поток 2 (логистика)
Реализация Потока 2 не входит в MVP. Для оценки/запуска требуется заполнить `logistics_api_matrix.md`.

