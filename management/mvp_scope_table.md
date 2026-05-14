# MVP Scope table — Поток 1 (Telegram-консультант)

## 1) MVP Scope statement

MVP (Поток 1) включает только Telegram-консультанта по подбору автомобиля: управляемый диалог, правила эскалации менеджеру, ответы по подтвержденной базе знаний, расчет стоимости в контуре калькулятора v1, минимальную админку (курсы/ставки/материалы/пользователи), хранилище диалогов/лидов/смет и формальные критерии приемки по UAT.

Основание и источники:
- `official_requirements_specification.md` (ключевые требования, роли, позиционирование/качество);
- `technical_assignment_tz.md` (разделение Поток 1 / Поток 2);
- `commercial_terms_final_cp_inputs.md` (коммерческие рамки и ограничения первого релиза);
- `decision_log.md` (обязательные решения и статусы).

## 2) MoSCoW (легенда)

- **Must** — обязательно для MVP и прохождения UAT в scope (`BOT-UAT-*`, `CALC-UAT-*`).
- **Should** — желательно для MVP, но допускается перенос без блокировки приемки при сохранении Must.
- **Could** — улучшение/опционально, реализуется при наличии времени без риска качества.
- **Won’t** — не входит в MVP (явно исключено / `deferred` на поток 2 / отдельное решение).

## 3) Scope table (In/Out)

| Area | In MVP (MoSCoW) | Out of MVP / Deferred (Won’t) | Source |
|---|---|---|---|
| Dialog | Must | — | RS-A-01, BOT-UAT-01 |
| Escalation | Must | — | RS-A-01, RS-A-05, D-007, BOT-UAT-04, BOT-UAT-07 |
| KB (Knowledge Base) | Must | Наполнение контентом заказчика (материалы KB-SRC-08/09) как обязательный объем — `deferred` | RS-A-02, D-005, BOT-UAT-05, BOT-UAT-07 |
| Calculator | Must | XLS 1:1 валидация алгоритма и множитель x1.02 — `deferred` | RS-A-03, D-001, D-002, D-003, D-004, CALC-UAT-01..07 |
| Admin | Must | Расширенная админка (аналитика/CRM/каналы уведомлений) — Won’t | RS-A-04, D-011, D-012 |
| Data & Leads | Must | CRM-интеграция (API/синхронизация) — Won’t; в MVP только реестр лидов v1 + экспорт CSV | D-011, BOT-UAT-09 |
| Audit & Logs | Must | — | RS-A-07, BOT-UAT-09 |
| QA & UAT | Must | UAT логистики — `deferred` | RS-A-06, BOT-UAT-01..09, CALC-UAT-01..07, D-010 |
| Release | Must | — | RS-A-06, RS-A-07 |
| Stream 2 (Logistics) | Won’t | Все `LOG-UAT-*`, выполнение API-матрицы 15 источников, выбор/интеграция 2–4 источников первой очереди — `deferred` | RS-B-xx (в подготовке), D-013..D-016, `logistics_api_matrix.md` |
| Notifications (non-Telegram) | Won’t | MAX/Email/SMS и иные каналы — `deferred` | D-012 |
| Manager panel UI | Won’t | Отдельная панель менеджера (вне Telegram) — `deferred` | `commercial_terms_final_cp_inputs.md`, BOT-UAT-08 (Telegram takeover) |

