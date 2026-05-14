# Traceability matrix (baseline)

## Требования Потока 1 (RS-A)

| Requirement ID | Требование (кратко) | Источник | Work items | UAT |
|---|---|---|---|---|
| RS-A-01 | Управляемый диалог + передача менеджеру | `official_requirements_specification.md` (Ключевые требования, п.1) | WI-BOT-002, WI-BOT-011, WI-BOT-012, WI-BOT-013, WI-BOT-014, WI-BOT-016, WI-DATA-010, WI-DATA-020 | BOT-UAT-01, BOT-UAT-02, BOT-UAT-04, BOT-UAT-06, BOT-UAT-07, BOT-UAT-08 |
| RS-A-02 | База знаний с контролем источников | `official_requirements_specification.md` (Ключевые требования, п.2) + `knowledge_base_corpus_register.md` | WI-ADMIN-030, WI-BOT-015 | BOT-UAT-05, BOT-UAT-07 |
| RS-A-03 | Расчетный модуль стоимости по формуле v1 | `official_requirements_specification.md` (Ключевые требования, п.3) + `calculator_formula_specification.md` | WI-CALC-010, WI-CALC-020, WI-ADMIN-010, WI-ADMIN-020 | BOT-UAT-03, CALC-UAT-01..07 |
| RS-A-04 | Роли и доступы (MVP) | `official_requirements_specification.md` (таблица ролей) | WI-ADMIN-040 | BOT-UAT-09 |
| RS-A-05 | Правила качества: нет источника/низкая уверенность → эскалация | `official_requirements_specification.md` (позиционирование/качество) + `decision_log.md` (D-007) | WI-BOT-012, WI-BOT-015, WI-CALC-020, WI-ADMIN-030 | BOT-UAT-05, BOT-UAT-07 |
| RS-A-06 | Формальные критерии приемки и UAT | `uat_acceptance_scenarios.md` | WI-QA-010, WI-QA-020, WI-REL-010 | BOT-UAT-01..09, CALC-UAT-01..07 |
| RS-A-07 | Все блокирующие решения имеют статус/владельца | `official_requirements_specification.md` (Ключевые требования, п.6) + `decision_log.md` | WI-BASE-010, WI-BASE-020 | — |
