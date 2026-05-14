# Effort & capacity model — MVP (7 weeks) + Stabilization (30 days)

Основание: `management/roadmap_7_weeks.md`, `management/backlog.md`, `commercial_terms_final_cp_inputs.md`.  
Scope: модель трудозатрат и загрузки по ролям (PMO governance). Не является сметой по фиксированной цене.

## 1) Assumptions (фиксируем как baseline)

| Параметр | Значение |
|---|---|
| Таймбокс MVP | 7 недель (Week 1..7) |
| Stabilization / Hypercare | 30 календарных дней после релиза; **defects-only** |
| Базовая рабочая неделя | 5 рабочих дней, 40 часов на 1 FTE |
| Роли в модели | Dev Lead, Requirements Owner, Solution Architect, Integration & Data Lead, QA/UAT Lead, PMO |
| Инженерная команда (аппроксимация) | **Integration & Data Lead = 1 Backend + 1 Fullstack = 2 FTE = 80h/week** |
| Диапазон (range) | Min = ML × 0.8; Max = ML × 1.25 |
| Оценка стабилизации в “неделях работ” | 30 календарных дней ≈ **4 рабочие недели** (20 рабочих дней) |

## 2) Capacity baseline (максимальная доступная мощность)

| Role | FTE baseline | Capacity (h/week) |
|---|---:|---:|
| Dev Lead | 1.0 | 40 |
| Requirements Owner | 1.0 | 40 |
| Solution Architect | 1.0 | 40 |
| Integration & Data Lead | 2.0 | 80 |
| QA/UAT Lead | 1.0 | 40 |
| PMO | 1.0 | 40 |

## 3) Week-by-week allocation defaults (MVP Weeks 1–7)

Формула для Most-likely (ML) по неделе: `Capacity(h/week) × Allocation%`.

| Role | W1 | W2 | W3 | W4 | W5 | W6 | W7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dev Lead | 40% | 50% | 40% | 40% | 35% | 35% | 50% |
| Requirements Owner | 60% | 50% | 30% | 20% | 20% | 15% | 20% |
| Solution Architect | 50% | 70% | 40% | 30% | 25% | 25% | 20% |
| Integration & Data Lead | 50% | 60% | 85% | 85% | 90% | 80% | 60% |
| QA/UAT Lead | 20% | 25% | 35% | 35% | 50% | 60% | 90% |
| PMO | 50% | 50% | 40% | 40% | 35% | 35% | 50% |

Примечание: значения заданы как управленческий baseline, чтобы не требовать доп. решений при стартовом планировании.

## 4) Stabilization allocation defaults (4 рабочие недели)

| Role | Allocation% | ML hours (per week) |
|---|---:|---:|
| Dev Lead | 20% | 8 |
| Requirements Owner | 10% | 4 |
| Solution Architect | 10% | 4 |
| Integration & Data Lead | 40% | 32 |
| QA/UAT Lead | 40% | 16 |
| PMO | 25% | 10 |

## 5) Effort by phase (person-hours; range Min / ML / Max)

Формулы:
- `ML (MVP) = Σ_week (Capacity × Allocation%)`
- `ML (Stabilization) = (Capacity × Allocation%) × 4`
- `Min = ML × 0.8`, `Max = ML × 1.25`

| Role | MVP (Min/ML/Max) | Stabilization (Min/ML/Max) | Total (Min/ML/Max) |
|---|---:|---:|---:|
| Dev Lead | 92.8 / 116.0 / 145.0 | 25.6 / 32.0 / 40.0 | 118.4 / 148.0 / 185.0 |
| Requirements Owner | 68.8 / 86.0 / 107.5 | 12.8 / 16.0 / 20.0 | 81.6 / 102.0 / 127.5 |
| Solution Architect | 83.2 / 104.0 / 130.0 | 12.8 / 16.0 / 20.0 | 96.0 / 120.0 / 150.0 |
| Integration & Data Lead | 326.4 / 408.0 / 510.0 | 102.4 / 128.0 / 160.0 | 428.8 / 536.0 / 670.0 |
| QA/UAT Lead | 100.8 / 126.0 / 157.5 | 51.2 / 64.0 / 80.0 | 152.0 / 190.0 / 237.5 |
| PMO | 96.0 / 120.0 / 150.0 | 32.0 / 40.0 / 50.0 | 128.0 / 160.0 / 200.0 |

**Итого (ML):** MVP = 960.0h; Stabilization = 296.0h; Total = 1256.0h.

## 6) How to use (операционно)

1) Каждую неделю фиксировать фактические часы по ролям в лидерском статусе: `management/weekly_status_template.md`.
2) При отклонении > 15% по любой роли или по total — поднимать риск/блокер и обновлять критический путь.
3) Любое расширение scope (в т.ч. “улучшения” в стабилизации) оформлять через решение в `decision_log.md`.

