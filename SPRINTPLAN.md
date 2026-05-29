# SPRINTPLAN.md

> Обновляется Orchestrator'ом в начале каждого цикла и Reviewer'ом в конце.  
> Задачи оформляются в стиле INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.

---

## Метаданные спринта

| Параметр | Значение |
|----------|----------|
| **Цикл №** | 0 |
| **Дата старта** | 2026-05-29 |
| **Цель спринта** | Завершить интеграцию Perplexity в Telegram-консультанта, актуализировать пользовательские инструкции, обеспечить надёжное локальное окружение для agentic разработки (включая smoke-режим) |

---

## Фазы и задачи

### Фаза 0 — Подготовка окружения и контекста (Orchestrator)

| # | Задача | Критерий приёмки | Статус |
|---|--------|------------------|--------|
| 0.1 | Запустить setup_kurbanov.ps1 (или с -Smoke) | .venv создана, зависимости установлены, python импорты работают | ☑ |
| 0.2 | Проверить git status и ветку | На feature/telegram-ai-consultant-perplexity, чистое дерево или только ожидаемые изменения | ☐ |
| 0.3 | Прочитать ключевые спецификации | TASK_SPECIFICATION.md + architecture/ai_consultant_instructions.md + management/telegram_ai_consultant_skill.md + docs/telegram_consultant_user_guide.md | ☐ |
| 0.4 | Обновить PROJECT_CONTEXT.md | Файл актуален, < 3000 токенов, отражает текущую фичу Perplexity | ☑ |
| 0.5 | Создать/обновить SPRINTPLAN.md | INVEST-задачи для всех фаз заполнены | ☑ |
| 0.6 | Настроить git user | `git config user.name` = "Евгений Чистяков", email корректен | ☐ |
| 0.7 | Инициализировать agentless_loop (Solver Loop) | Созданы agentless_loop/README.md + SOLVER_LOOP.md, AGENTS.md указывает на лёгкий режим как основной для прямой работы | ☑ |

---

### Фаза 1 — Актуализация документации и инструкций (Coder + Reviewer)

| # | Задача | Критерий приёмки | Статус |
|---|--------|------------------|--------|
| 1.1 | Проверить и доработать docs/telegram_consultant_user_guide.md | Документ полон, соответствует реальному поведению бота и калькулятора | ☑ (ГОТОВО: добавлено 6 реальных многоходовых примеров в разделе 8.7, покрыты happy path + budget_below_threshold + non_standard_scope + manager_requested + low_confidence + post_qualification_message. Полностью соответствуют коду и architecture/ai_consultant_instructions.md) |
| 1.2 | Синхронизировать management/user_guide.md, operator_guide.md, administrator_guide.md с новой Perplexity-логикой | Нет противоречий с ai_consultant_instructions.md | ☑ (operator_guide + administrator_guide обновлены по A.2; user_guide уже синхронизирован в A.1) |
| 1.3 | Обновить архитектурные инструкции при необходимости | architecture/ai_consultant_instructions.md отражает текущие эскалации и grounded-правила | ☐ |
| 1.4 | Добавить/актуализировать тесты на perplexity_client и dialog_engine | Тесты проходят в smoke-режиме | ☐ |
| 1.5 | Коммит документации и тестов | Сообщение на естественном русском, human-like | ☐ |

---

### Фаза 2 — Улучшение интеграции и качества Perplexity (Coder → Tester → Debugger)

| # | Задача | Критерий приёмки | Статус |
|---|--------|------------------|--------|
| 2.1 | Проанализировать текущую реализацию perplexity_client.py и consultant.py | Понимание промптов, истории, обработки ошибок, fallback'ов | ☑ (частично: perplexity_client переведён на action=escalate + конкретные reasons; тесты обновлены и расширены) |
| 2.2 | Улучшить обработку ответов модели (парсинг, валидация, эскалация при низкой уверенности) | Соответствует правилам из architecture/ai_consultant_instructions.md | ☑ (B.2: улучшена передача контекста + WARNING логи в роутере; B.1 клиент теперь всегда escalate) |
| 2.3 | Добавить/расширить тесты на идемпотентность и edge-кейсы диалога с Perplexity | Покрытие ключевых сценариев >80% | ☐ |
| 2.4 | Реализовать/улучшить механизм передачи менеджеру (takeover) при сбоях модели | Сценарии из skill.md покрыты | ☐ |
| 2.5 | Проверить работу в smoke-режиме (без реального ключа Perplexity) | Консультант gracefully переходит в rule-based | ☐ |
| 2.6 | Коммит улучшений | Чистый коммит на русском | ☐ |

---

### Фаза 3 — Валидация и подготовка к merge (Tester + Reviewer)

| # | Задача | Критерий приёмки | Статус |
|---|--------|------------------|--------|
| 3.1 | Полный прогон тестов | `pytest -q services/consultant_api/tests` — все зелёные (в т.ч. smoke) | ☐ |
| 3.2 | Статический анализ | `ruff check services/consultant_api` чистый | ☐ |
| 3.3 | Smoke HTTP-проверка (локально) | / , /intake, /calculator, /admin, /telegram/webhook (симуляция) работают | ☐ |
| 3.4 | Ревью соответствия спецификациям | Нет отклонений от ai_consultant_instructions и user_guide | ☐ |
| 3.5 | Обновить PROJECT_CONTEXT.md и SPRINTPLAN.md итогами цикла | lessons_learned записаны, новые правила добавлены при необходимости | ☐ |
| 3.6 | Подготовить merge в main (если задача завершена) | git checkout main; git merge ... ; тесты на main | ☐ |

---

## Следующие шаги (после завершения цикла 0)

- Актуализировать TASK_SPECIFICATION.md под конкретные доработки Perplexity (если есть открытые задачи в backlog).
- При необходимости добавить dedicated роли или расширить TOOLS_REGISTRY (например, для работы с Telegram API в тестах).
- После 2–3 циклов — провести architecture review изменений в dialog_engine и consultant.

---

**Примечание для агента:** Все задачи должны выполняться инкрементально, с коммитами после значимых шагов. Перед любым большим изменением — bootstrap окружения.