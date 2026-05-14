# Dependency register + critical path — MVP → Stabilization → Phase 2

Основание: `management/blocker_register.md`, `decision_log.md`, `management/backlog.md`, `management/roadmap_7_weeks.md`,
`logistics_api_matrix.md`, `management/go_no_go_checklist.md`, `architecture/risk_register.md`.

Назначение: единый источник правды по зависимостям и критическому пути (PMO governance).  
Правило: зависимости, блокирующие **Start UAT** или **Release MVP**, считаются **CRITICAL**.

## 1) Dependency register

Статусы (единый словарь): `open` / `waiting_customer` / `in_progress` / `resolved` / `deferred`.

| DEP-ID | Type | Description | Blocks milestone | Needed by (Week #) | Owner | Status | Impact | Probability | Mitigation / Next action | Source link |
|---|---|---|---|---:|---|---|---|---|---|---|
| DEP-EXT-001 | External | `TELEGRAM_BOT_TOKEN` предоставлен для окружения UAT/релиза | Start UAT; Release MVP | 3 | Заказчик, Дмитрий | waiting_customer | High | High | Предоставить токен + проверить webhook интеграцию в тестовом чате | BR-003 |
| DEP-EXT-002 | External | `TELEGRAM_MANAGER_CHAT_ID` подтвержден (куда слать эскалации) | Complete UAT; Release MVP | 4 | Заказчик, Дмитрий | open | High | Medium | Подтвердить чат/канал и протестировать уведомления менеджеру | BR-005 |
| DEP-EXT-003 | External | KB материалы заказчика (FAQ, KB-SRC-08) предоставлены и промодерированы | Complete UAT | 6 | Заказчик, Дмитрий | waiting_customer | Medium | High | Предоставить материалы; загрузить в KB; довести часть документов до `approved` | BR-001, D-005 |
| DEP-EXT-004 | External | KB материалы заказчика (обезличенные диалоги, KB-SRC-09) предоставлены | Complete UAT | 6 | Заказчик, Дмитрий | waiting_customer | Medium | High | Подготовить выгрузку/обезличивание и правила модерации | BR-002 |
| DEP-INT-001 | Internal | Контракты/политики и NFR baseline зафиксированы (AS-IS/TO-BE + GAP) | Start UAT | 2 | Solution Architect | in_progress | High | Medium | Довести артефакты до согласованного baseline (см. `architecture/*`) | WI (Week 2), `architecture/api_contracts.md` |
| DEP-INT-002 | Internal | Идемпотентность webhook и “no side-effects on retry” | Release MVP | 4 | Dev Lead | open | High | High | Реализовать дедупликацию и тестовые кейсы; закрыть R-001 | `architecture/risk_register.md` R-001 |
| DEP-INT-003 | Internal | Admin безопасность: `ADMIN_API_TOKEN` обязателен вне dev + правило ротации | Start UAT; Release MVP | 6 | Dev Lead | open | High | Medium | Зафиксировать policy генерации/хранения/ротации; обновить env в stage/prod | BR-006 |
| DEP-INT-004 | Internal | UAT пакет готов (traceability, suites, протоколы, Go/No-Go) | Start UAT | 6 | QA/UAT Lead | in_progress | High | Medium | Синхронизировать `management/*` и проверить непротиворечивость ID | WI-QA-010, WI-QA-020 |
| DEP-INT-005 | Internal | Решения по логистике D-013..D-016 закрыты или явно `deferred` с ограничениями | Phase 2 Go | S4 | PMO | deferred | High | Medium | Перед Phase 2: актуализировать `logistics_api_matrix.md` и статусы решений | D-013..D-016 |
| DEP-EXT-005 | External | Поток 2: перечень источников + подтверждение ToS/право + выбор 2–4 источников первой очереди | Phase 2 Go | S4 | Заказчик, Тамара | deferred | High | High | Заполнить матрицу; выбрать источники; зафиксировать допустимую стратегию интеграции | BR-007, BR-008, `logistics_api_matrix.md` |

Примечание по `Needed by`: для стабилизации используем обозначения S1..S4 (4 рабочие недели).

## 2) Critical Path View (обновлять еженедельно)

### CRITICAL (блокирует Start UAT или Release MVP)
- DEP-EXT-001 — Telegram токен для реальной интеграции и UAT канала.
- DEP-EXT-002 — Manager chat id для эскалаций (UAT и коммерческая ценность MVP).
- DEP-INT-002 — идемпотентность webhook (риск дублей/спама/ложной аналитики).
- DEP-INT-003 — защита admin endpoints (неприемлемо вне dev).
- DEP-INT-004 — готовность UAT пакета (без протокола/сьютов UAT “не стартует”).

### NEXT (влияет на качество/приемку, но не всегда блокирует старт)
- DEP-EXT-003 / DEP-EXT-004 — KB материалы заказчика (покрытие ответов vs рост эскалаций).

### Phase 2 gates (после стабилизации)
- DEP-EXT-005 + DEP-INT-005 — readiness gates потока 2 по источникам/ToS/SLA/решениям.

