# UAT execution report — template (MVP Поток 1)

**Назначение:** единый шаблон протокола выполнения UAT (результаты + evidence + подписи).

**Источник UAT сценариев:** `uat_acceptance_scenarios.md`
> Примечание: если `uat_acceptance_scenarios.md` еще не содержит `CALC-UAT-*`, строки `CALC-UAT-*` ниже заполняются как `blocked`/`n/a`
> до фиксации UAT baseline.

**Дата:** YYYY-MM-DD  
**Версия релиза:** vX.Y (или git tag/commit)  
**Окружение:** dev/stage/prod (описать)  

## 1) Baselines перед началом UAT (обязательные фиксации)
- Формула калькулятора: версия + источник (`calculator_formula_specification.md`) + timestamp
- FX: источник курсов + политика override + `fetched_at`/`rate_date`
- KB: список источников + статусы модерации (`approved/draft/...`) + версия корпуса
- Роли/доступы: список ролей/пользователей, применимый `ADMIN_API_TOKEN` режим (dev/prod)
- Решения/блокеры: ключевые `D-*` влияющие на UAT (из `decision_log.md`)

## 2) Scope UAT
- В scope: перечислить `BOT-UAT-*` / `CALC-UAT-*` сценарии
- Out of scope: перечислить исключенные сценарии (если есть) + основание (ссылка на RS/WI/решение)

## 3) Результаты по сценариям
Таблица заполняется на каждый сценарий.

| UAT ID | Сценарий | Исполнитель | Дата/время | Результат (pass/fail/blocked) | Evidence (ссылка/артефакт) | Дефекты (IDs) | Notes |
|---|---|---|---|---|---|---|---|
| BOT-UAT-01 |  |  |  |  |  |  |  |
| BOT-UAT-02 |  |  |  |  |  |  |  |
| BOT-UAT-03 |  |  |  |  |  |  |  |
| BOT-UAT-04 |  |  |  |  |  |  |  |
| BOT-UAT-05 |  |  |  |  |  |  |  |
| BOT-UAT-06 |  |  |  |  |  |  |  |
| BOT-UAT-07 |  |  |  |  |  |  |  |
| BOT-UAT-08 |  |  |  |  |  |  |  |
| BOT-UAT-09 |  |  |  |  |  |  |  |
| CALC-UAT-01 |  |  |  |  |  |  |  |
| CALC-UAT-02 |  |  |  |  |  |  |  |
| CALC-UAT-03 |  |  |  |  |  |  |  |
| CALC-UAT-04 |  |  |  |  |  |  |  |
| CALC-UAT-05 |  |  |  |  |  |  |  |
| CALC-UAT-06 |  |  |  |  |  |  |  |
| CALC-UAT-07 |  |  |  |  |  |  |  |

## 4) Сводка дефектов
| Defect ID | Severity | Summary | Статус | Owner | Ссылка на RS/WI/UAT | Notes |
|---|---:|---|---|---|---|---|
|  |  |  |  |  |  |  |

## 5) Go/No-Go решение
- Проверка по `management/go_no_go_checklist.md`: pass/fail + ссылки на evidence
- Открытые Severity 1/2 дефекты: 0 / N (если N > 0 → No-Go)
- Known issues Severity 3/4 (если есть): перечислить и сослаться на `management/release_notes_v1.md`

## 6) Подписи (sign-off)
- Заказчик: ФИО / дата / подпись
- Дмитрий: ФИО / дата / подпись
- Тамара (если применимо): ФИО / дата / подпись
- Руководитель разработки: ФИО / дата / подпись
