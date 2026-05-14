# Release notes — MVP Поток 1 (draft)

**Дата:** YYYY-MM-DD  
**Версия:** v1.0  

## Scope
- Telegram-консультант: управляемый диалог, эскалация менеджеру, takeover `/resume_bot`
- Калькулятор v1 (контур РФ, 3–5 лет, до 160 л.с.)
- База знаний: структура, модерация источников, правила качества
- Admin API: курсы/ставки/контент/пользователи/роли
- Журналирование: диалог/расчет/эскалация/действия менеджера

## Work items
- `WI-...`

## Validation evidence
- UAT: BOT-UAT-01..09, CALC-UAT-01..07
- Критерий: Severity 1/2 = 0 (см. `uat_acceptance_scenarios.md`)
- Команды:
  - `pytest -q`

## Known limitations / deferred
- Поток 2 (логистика): `deferred` до заполнения `logistics_api_matrix.md`
- Контент заказчика (KB-SRC-08/09): поставка отдельно; без контента — эскалация по правилам качества

