# API contracts — MVP Поток 1 (baseline)

Источник: `official_requirements_specification.md`, `calculator_formula_specification.md`, `uat_acceptance_scenarios.md`.

## Telegram ingress
- `POST /telegram/webhook`
  - Input: Telegram update JSON
  - Headers: `X-Telegram-Bot-Api-Secret-Token` (если включен `TELEGRAM_WEBHOOK_SECRET_TOKEN`)
  - Behavior:
    - пишет `audit_events` (event_type=`telegram.update`)
    - пишет `messages` (direction=`in`)
    - при сообщении менеджера: `bot.pause` / `bot.resume` и флаг `conversations.bot_paused`
    - при сборе параметров: задает следующий вопрос
    - при завершении квалификации: уведомляет менеджера

## Admin API (минимум MVP)
Все endpoints требуют `X-Admin-Token`, если задан `ADMIN_API_TOKEN`.

- `GET /admin/health`
- `POST /admin/fx_rates/refresh`
- `GET /admin/fx_rates?rate_date=YYYY-MM-DD`
- `POST /admin/fx_rates/override`
- `GET /admin/fx_rates/overrides`
- `POST /admin/rates`
- `GET /admin/rates`
- `POST /admin/estimates/preview`
- `POST /admin/kb_sources`
- `GET /admin/kb_sources`
- `POST /admin/kb_docs`
- `GET /admin/kb_docs?source_code=...`
- `POST /admin/roles`
- `GET /admin/roles`
- `POST /admin/users`
- `GET /admin/users`
- `GET /admin/leads/export.csv`

## Валидация / Acceptance
Baseline проверки: сценарии `BOT-UAT-*` и `CALC-UAT-*` из `uat_acceptance_scenarios.md`.
