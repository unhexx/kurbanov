# Backlog (baseline) — MVP Telegram-консультанта (Поток 1)

Источник требований: `official_requirements_specification.md`, `technical_assignment_tz.md`, `decision_log.md`, `calculator_formula_specification.md`, `knowledge_base_corpus_register.md`, `uat_acceptance_scenarios.md`.

## Epic: WI-BASE-001 — Repo bootstrap + baseline управления
- Scope: структура repo (docs+code), схема трассируемости, DoR/DoD, RAID, roadmap, статус-шаблон
- Links: RS-A-01..RS-A-07 (см. `management/traceability_matrix.md`)
- UAT: BOT-UAT-09 (аудит/журналирование как проверяемый контур)

## Epic: WI-BOT-001 — Telegram ingress + аудит входящих событий
- Scope: `POST /telegram/webhook`, валидация webhook secret, запись `audit_event`
- Links: RS-A-01, RS-A-05, D-007, BOT-UAT-09
- UAT: BOT-UAT-09

## Epic: WI-BOT-010 — Диалог (15 параметров) и эскалация
- Story: WI-BOT-011 — Первичная квалификация (сбор параметров)
  - Links: RS-A-01, BOT-UAT-01
  - UAT: BOT-UAT-01
- Story: WI-BOT-012 — Нестандартный кейс → эскалация
  - Links: RS-A-01, RS-A-05, BOT-UAT-04, BOT-UAT-07
  - UAT: BOT-UAT-04, BOT-UAT-07
- Story: WI-BOT-013 — Правило takeover менеджером + `/resume_bot`
  - Links: RS-A-01, BOT-UAT-08
  - UAT: BOT-UAT-08

## Epic: WI-CALC-001 — Калькулятор v1 (контур РФ, 3–5 лет, до 160 л.с.)
- Story: WI-CALC-010 — Расчет и смета с версией/курсами/timestamp
  - Links: RS-A-03, D-003, D-004, CALC-UAT-01, BOT-UAT-03
  - UAT: CALC-UAT-01, BOT-UAT-03
- Story: WI-CALC-020 — Валидация контура v1 и причины эскалации
  - Links: D-003, CALC-UAT-03..06
  - UAT: CALC-UAT-03, CALC-UAT-04, CALC-UAT-05, CALC-UAT-06

## Epic: WI-ADMIN-001 — Admin API (минимум MVP)
- Story: WI-ADMIN-010 — CRUD курсов валют + override
  - Links: D-004, CALC-UAT-06
  - UAT: CALC-UAT-06
- Story: WI-ADMIN-020 — CRUD ставок/справочников
  - Links: RS-A-03, calculator_formula_specification.md (раздел 4)
  - UAT: CALC-UAT-01
- Story: WI-ADMIN-030 — CRUD базы знаний (источники/документы) + статусы модерации
  - Links: RS-A-02, D-007, knowledge_base_corpus_register.md
  - UAT: BOT-UAT-05, BOT-UAT-07
- Story: WI-ADMIN-040 — Пользователи/роли (RBAC)
  - Links: RS-A-04
  - UAT: BOT-UAT-09 (журналирование действий)

## Epic: WI-DATA-001 — Хранилище диалогов/лидов/смет/эскалаций + экспорт
- Story: WI-DATA-010 — Каноническая модель данных и миграции
  - Links: RS-A-01..RS-A-05
  - UAT: BOT-UAT-09
- Story: WI-DATA-020 — Реестр лидов v1 + экспорт CSV
  - Links: D-011
  - UAT: BOT-UAT-09

## Epic: WI-QA-001 — Traceability + quality gates + Go/No-Go
- Links: `uat_acceptance_scenarios.md` (разделы 1 и 4)
- UAT: все BOT-UAT и CALC-UAT в scope MVP

## Epic: WI-REL-001 — Release notes + фиксация baseline
- Scope: `management/release_notes_v1.md`, сбор доказательств, checklist
- UAT: подписанный протокол + Severity 1/2 = 0

