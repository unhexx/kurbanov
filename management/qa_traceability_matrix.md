# QA Traceability matrix (detailed) — MVP Поток 1

**Назначение:** детализация трассируемости в формате **Requirement (`RS-*`) → Test Case (`TC-*`) → UAT scenario (`BOT-UAT-*`/`CALC-UAT-*`) → Evidence/Status**.

**Источники правды:**
- Идентификаторы и правила ссылок: `management/traceability_scheme.md`
- Базовая матрица RS → WI → UAT: `management/traceability_matrix.md`
- UAT baseline и Severity policy: `uat_acceptance_scenarios.md`

**Дата актуализации:** 14.05.2026

## Правила заполнения
1) `TC-*` — стабильный идентификатор тест-кейса. Рекомендуемый формат: `TC-<AREA>-NNN`, где `<AREA>` ∈ `{BASE,BOT,CALC,ADMIN,DATA,REL,QA}`.
2) `Evidence` — ссылка на артефакт проверки (лог, команда, отчет UAT, скриншот, CSV, запись в release notes). Минимум:
   - UAT: заполненный отчет по шаблону `management/uat_execution_report_template.md` (как отдельный файл вида `management/uat_execution_report_YYYY-MM-DD.md`).
3) `Status` — одно из: `planned`, `in_progress`, `passed`, `failed`, `blocked`, `n/a`.
4) Матрица **не должна противоречить** `management/traceability_matrix.md` (RS→WI→UAT). При расхождениях — фиксировать GAP/Blocker.

## Матрица (seed)

| RS | Требование (кратко) | TC | Test case (кратко) | UAT | Evidence | Status | Notes |
|---|---|---|---|---|---|---|---|
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-001 | Первичная квалификация (15 параметров) | BOT-UAT-01 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-002 | Бюджет ниже порога: корректная коммуникация/эскалация | BOT-UAT-02 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-003 | Нестандартный расчет: эскалация с причиной и контекстом | BOT-UAT-04 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-004 | Подбор альтернатив: shortlist или эскалация при нехватке данных | BOT-UAT-06 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-005 | Неизвестный вопрос: запрет “выдумывать” → эскалация | BOT-UAT-07 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-01 | Управляемый диалог + передача менеджеру | TC-BOT-006 | Takeover менеджером: пауза бота и `/resume_bot` | BOT-UAT-08 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-02 | База знаний с контролем источников | TC-BOT-007 | Ответ только из `approved` источников; иначе эскалация | BOT-UAT-05 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-02 | База знаний с контролем источников | TC-BOT-008 | KB miss: отсутствует ответ → эскалация | BOT-UAT-07 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-001 | Расчет “под ключ” в контуре v1 (в сообщении бота) | BOT-UAT-03 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-002 | Калькулятор: базовая корректность (контур v1) | CALC-UAT-01 | — | blocked | `uat_acceptance_scenarios.md` пока не содержит определения `CALC-UAT-*` (требуется добавить перед UAT). |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-003 | Калькулятор: версионность формулы + fx timestamp | CALC-UAT-02 | — | blocked |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-004 | Калькулятор: проверки scope (страна/возраст/мощность) | CALC-UAT-03 | — | blocked |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-005 | Калькулятор: round/format и сумма items = total | CALC-UAT-04 | — | blocked |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-006 | Калькулятор: устойчивость к невалидным входам | CALC-UAT-05 | — | blocked |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-007 | Калькулятор: FX override политика | CALC-UAT-06 | — | blocked |  |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | TC-CALC-008 | Калькулятор: воспроизводимость “offer snapshot” | CALC-UAT-07 | — | blocked |  |
| RS-A-04 | Роли и доступы (MVP) | TC-ADMIN-001 | RBAC в админке + контроль доступа к выгрузкам | BOT-UAT-09 | `management/uat_execution_report_YYYY-MM-DD.md` | planned |  |
| RS-A-05 | Правила качества: нет источника/низкая уверенность → эскалация | TC-QA-001 | Quality gate: неподтвержденный ответ запрещен → эскалация | BOT-UAT-05 | `management/uat_execution_report_YYYY-MM-DD.md` | planned | Связать с решением `D-007` (см. `decision_log.md`). |
| RS-A-06 | Формальные критерии приемки и UAT | TC-QA-002 | Gate: UAT подписан + Sev1/2 = 0 + evidence pack | BOT-UAT-01..09 | `management/go_no_go_checklist.md` + `management/uat_execution_report_YYYY-MM-DD.md` | planned | CALC-UAT блокируется до появления определений. |
| RS-A-07 | Все блокирующие решения имеют статус/владельца | TC-BASE-001 | Проверка `decision_log.md`: все блокеры имеют статус/владельца | — | `decision_log.md` | planned |  |
