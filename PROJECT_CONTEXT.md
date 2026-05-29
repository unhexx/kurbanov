# PROJECT_CONTEXT.md

> **Источник истины:** `TASK_SPECIFICATION.md` + архитектурные документы консультанта  
> Этот файл обновляется Orchestrator'ом (статус) и Reviewer'ом (лог саморазвития).  
> Максимальный объём: ~3000 токенов. При превышении — сжать старые записи.

---

## Идентификация проекта

| Параметр | Значение |
|----------|----------|
| **Проект** | kurbanov — MVP Telegram-консультант + веб-портал автоподбора (Exception.Expert) |
| **Цель** | Развитие и поддержка Telegram-бота консультанта по подбору автомобилей (3-5 лет, до 160л.с., РФ/РБ/КЗ), веб-анкеты, калькулятора стоимости, админки. Интеграция Perplexity для генерации ответов (текущая фича). |
| **Стек** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 + psycopg, PostgreSQL 16, httpx, Jinja2, Perplexity API (sonar-pro), pytest, ruff, Docker Compose |
| **Ветка** | feature/telegram-ai-consultant-perplexity |
| **Git user** | Евгений Чистяков <echistyakov@aq.ru> |
| **Root** | X:\LocalRepo\kurbanov |

---

## Текущий статус

| Поле | Значение |
|------|----------|
| **Цикл №** | 0 |
| **Текущая фаза** | инициализация окружения + планирование |
| **Текущая роль** | Orchestrator |
| **Статус** | IN_PROGRESS |
| **Уверенность** | 0.85 |
| **Последний коммит** | 92e4653 — Руководитель разработки: Добавлена пользовательская инструкция Telegram-консультанта для заказчика и операторов |
| **Дата обновления** | 2026-05-29 |

---

## Ключевые файлы

```
X:\LocalRepo\kurbanov\
├── TASK_SPECIFICATION.md          ← источник истины для агента (создать/актуализировать)
├── PROJECT_CONTEXT.md             ← этот файл
├── SPRINTPLAN.md                  ← план текущего спринта
├── agentic_loop_template/         ← окружение agentic loop (адаптировано)
│   ├── SYSTEM_PROMPT.md
│   ├── setup_kurbanov.ps1         ← основной bootstrap для проекта
│   └── ...
├── services/consultant_api/
│   ├── app/
│   │   ├── main.py, routers/telegram.py, routers/admin.py
│   │   ├── services/{consultant.py, dialog_engine.py, perplexity_client.py, calculator.py}
│   │   └── web/...
│   ├── pyproject.toml (ruff/pytest)
│   ├── requirements.txt + requirements-dev.txt
│   └── tests/
├── architecture/ai_consultant_instructions.md
├── management/telegram_ai_consultant_skill.md
├── docs/telegram_consultant_user_guide.md   ← новая (2026-05)
├── docker-compose.yml
└── README.md
```

---

## Краткая история циклов

| Цикл | Роль | Фаза | Статус | Что сделано |
|------|------|------|--------|-------------|
| 0 | Orchestrator | инициализация | — | Созданы/адаптированы agentic_loop_template/, setup_kurbanov.ps1, PROJECT_CONTEXT.md, SPRINTPLAN.md. Заполнен SYSTEM_PROMPT. Подготовлено окружение. |

---

## Ключевые решения и обоснования

- Выбрана модель Perplexity (sonar-pro) для генерации ответов консультанта вместо rule-based (см. architecture и недавние изменения).
- Вся бизнес-логика (калькулятор v1, матрица эскалаций, правила grounded-ответов) остаётся детерминированной.
- Для локальной разработки без Docker/Postgres используется smoke-режим на SQLite (см. setup_kurbanov.ps1 -Smoke и README проекта).
- Коммиты и комментарии в коде — исключительно на естественном русском, голос реального разработчика (без упоминания ИИ/агентов).

---

## Известные ограничения и риски

- Калькулятор ограничен: оформление в РФ, возраст 3-5 лет, мощность ≤160 л.с. (FORMULA_VERSION=v1.0 по умолчанию).
- При пустом PERPLEXITY_API_KEY консультант работает в rule-based режиме (задаёт вопросы анкеты без внешнего сервиса).
- Требуется .env с реальными ключами (TELEGRAM_BOT_TOKEN, PERPLEXITY_API_KEY, ADMIN_API_TOKEN и др.) — gitignored.
- В smoke-режиме некоторые интеграции (курсы ЦБ, внешние) могут быть ограничены.

---

## Agent Performance Self-Improvement Log

### Цикл 0 — Инициализация окружения agentic loop

**Что сработало хорошо:**
- Успешно адаптирован шаблон из X:\LocalRepo\eegent под структуру проекта (код в services/consultant_api/, специфичный bootstrap).
- Создана удобная точка входа setup_kurbanov.ps1 с поддержкой -Smoke.
- Заполнены все плейсхолдеры SYSTEM_PROMPT реальными данными проекта.

**Что было неэффективно:**
- Шаблон содержал много примеров из других проектов (leak-data-importer) — потребовалась ручная адаптация путей и описаний.

**Новые постоянные правила (из lessons_learned):**
1. Перед каждым циклом обязательно вызывать `powershell -ExecutionPolicy Bypass -File .\agentic_loop_template\setup_kurbanov.ps1` (или с -Smoke).
2. Всегда активировать .venv и устанавливать `$env:PYTHONPATH = 'services\consultant_api'` перед запуском uvicorn/pytest.
3. При работе с Telegram-консультантом перечитывать architecture/ai_consultant_instructions.md и management/telegram_ai_consultant_skill.md.

**Рекуррентные проблемы:**
- (пока нет)

---

## Постоянные правила (применяются всегда)

1. Перед каждым циклом перечитывать `TASK_SPECIFICATION.md` (или эквивалентные архитектурные инструкции консультанта) полностью.
2. Не коммитить сломанный код — только рабочие состояния с прошедшими тестами.
3. `issues_found` в handoff JSON — не пропускать ни одну найденную проблему.
4. При `confidence < 0.7` — не передавать управление следующему агенту, сначала устранить неопределённость.
5. Все комментарии в коде, docstrings и git-коммиты — только на естественном русском языке в стиле mid/senior разработчика проекта (Евгений Чистяков). Запрещено упоминать AI/LLM/агент/MiniMax/Grok в коммитах и комментариях.
6. Для быстрых локальных проверок без поднятия PostgreSQL использовать smoke SQLite (setup с флагом -Smoke).
7. После `git pull` или смены ветки — повторно запускать bootstrap окружения.

*(дополнять по мере кристаллизации новых правил Reviewer'ом)*