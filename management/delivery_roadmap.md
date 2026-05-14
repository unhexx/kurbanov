# Delivery roadmap — MVP → Stabilization → Phase 2 (PMO baseline)

Основание: `management/roadmap_7_weeks.md`, `management/backlog.md`, `management/go_no_go_checklist.md`,
`management/weekly_status_template.md`, `management/blocker_register.md`, `decision_log.md`,
`commercial_terms_final_cp_inputs.md`, `logistics_api_matrix.md`.

Формат: относительные недели (Week 1..7) + gate-based этапы после релиза.  
Scope: управление сроками/вехами, зависимостями и отчетностью. Не описывает техдизайн.

## 0) Baseline (зафиксировано)

- MVP Поток 1 (Telegram-консультант): **7 недель** (`commercial_terms_final_cp_inputs.md`).
- Stabilization / Hypercare: **30 календарных дней после релиза MVP**, **defects-only** (без фич).
- Поток 2 (логистика): **после стабилизации**, только по readiness gates (без дат).

## 1) Phase: MVP (Weeks 1–7)

Детальный недельный план — источник правды: `management/roadmap_7_weeks.md`.  
Ниже — те же вехи + измеримые gates (entry/exit), чтобы управлять критическим путем и готовностью к UAT/релизу.

| Week | Фокус | Entry gate (что должно быть готово на старте) | Exit gate (measurable) |
|---:|---|---|---|
| 1 | Phase 0 — baseline + bootstrap | Зафиксированы коммерческие рамки и scope MVP (см. `commercial_terms_final_cp_inputs.md`, `management/mvp_scope_table.md`) | Backlog + DoR/DoD + traceability baseline опубликованы; каркас поднят (см. `management/backlog.md`, `management/definitions_ready_done.md`, `management/traceability_matrix.md`) |
| 2 | Phase 1 — архитектура и контракты | Week 1 exit выполнен | Зафиксированы контракты/политики (AS-IS/TO-BE) и NFR baseline; риски и GAP отражены (см. `architecture/api_contracts.md`, `architecture/nfr_checklist.md`, `architecture/risk_register.md`) |
| 3 | Phase 2 — диалог v1 | Week 2 exit выполнен | Демонстрация BOT-UAT-01 (минимальный диалог + сохранение/аудит событий в scope) |
| 4 | Phase 2 — takeover + эскалация | Week 3 exit выполнен | Демонстрация BOT-UAT-04, BOT-UAT-07, BOT-UAT-08; журналирование BOT-UAT-09 в базовом виде |
| 5 | Phase 3 — калькулятор v1 | Week 4 exit выполнен | Демонстрация CALC-UAT-01..06; смета с версией/курсами/timestamp (воспроизводимость) |
| 6 | Phase 3 — admin baseline | Week 5 exit выполнен | CRUD курсов/ставок/KB; RBAC baseline; UAT пакет подготовлен (см. `management/go_no_go_checklist.md`, `management/test_suite_catalog.md`, `management/uat_execution_report_template.md`) |
| 7 | Phase 4 — UAT + релизная стабилизация | Выполнен “UAT-ready” gate (см. ниже) | Пройдено BOT-UAT-01..09 и CALC-UAT-01..07; **Severity 1/2 = 0**; релиз-ноты и протокол UAT готовы (см. `management/release_notes_v1.md`) |

### UAT-ready gate (фиксируем перед стартом Week 7)

Считаем систему “готовой к UAT”, если одновременно выполнено:
1) UAT scope подтвержден и трассируем: `management/traceability_matrix.md` и `management/qa_traceability_matrix.md` не противоречат друг другу.
2) Go/No-Go критерии актуальны и измеримы: `management/go_no_go_checklist.md`.
3) Наборы прогонов определены: `management/test_suite_catalog.md` (Smoke/Regression/UAT) + правила запуска.
4) Шаблон протокола UAT готов: `management/uat_execution_report_template.md`.
5) Внешние блокеры, критичные для UAT/релиза, имеют план закрытия и владельца: `management/dependency_register.md` (Critical Path View).

## 2) Phase: Stabilization / Hypercare (30 календарных дней после релиза MVP)

Правило: **defects-only**. Любые изменения, которые выглядят как “фича/улучшение”, требуют отдельного решения и не входят в стабилизацию по умолчанию.

### Цели (objectives)
- Снижение дефектов и стабилизация UX: triage → fix → verify по `management/defect_policy.md`.
- Мониторинг baseline и эксплуатационная управляемость: health-checks, алерты, инструкции реакции.
- Повышение надежности релиза: правила hotfix/release cadence и контроль регрессий.
- Приведение отчетности к устойчивому режиму: еженедельный лидерский отчет по `management/weekly_status_template.md`.

### Выходные критерии (exit criteria)
- Открытые дефекты **Severity 1/2 = 0** (и отсутствуют повторные инциденты по тем же причинам).
- Выполнен минимальный ops-checklist (мониторинг/алерты/backup-проверка/процедуры деплоя — в объеме MVP).
- Еженедельная отчетность ведется 4 недели подряд без пропусков (есть факты по вехам/рискам/критическому пути).

### Контрольная сетка (рекомендуемая, без дат)
- Week S1: triage backlog дефектов + быстрые фиксы критичных; проверка метрик и логирования.
- Week S2: закрытие повторяющихся дефектов; hardening эксплуатационных процедур.
- Week S3: регрессионные прогоны; проверка “no Sev1/2 open”.
- Week S4: финальный стабилизационный отчет + Phase 2 Go/No-Go подготовка (см. ниже).

## 3) Phase 2 (Logistics) — gate-based (без сроков)

Поток 2 запускается только после стабилизации MVP и прохождения readiness gates. Источник правды: `logistics_api_matrix.md`,
`decision_log.md`, `management/blocker_register.md`, `management/dependency_register.md`.

### Readiness gates (обязательные)
1) **Источники**: заполнены и подтверждены 2–4 источника первой очереди (см. `logistics_api_matrix.md`; BR-007/BR-008).
2) **ToS/право**: по выбранным источникам подтверждена допустимость способа интеграции (API/parsing) и риски зафиксированы.
3) **SLA обновления**: зафиксирован SLA обновления данных (D-016 в `decision_log.md` — `resolved` или явно `deferred` с ограничениями).
4) **Решения D-013..D-016**: имеют финальные статусы `resolved/deferred` с явным влиянием на scope и цену.

### Go/No-Go checkpoint (после стабилизации)

Решение “Phase 2 Go” принимается на основании:
- KPI snapshot MVP (минимум: кол-во диалогов/лидов, доля эскалаций и причины, дефекты Sev1/2/3 динамика, стабильность релизов);
- актуального критического пути Phase 2 (`management/dependency_register.md`);
- подтверждения заказчиком/Тамарой операционной ценности источников первой очереди.

