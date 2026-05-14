# Схема трассируемости (baseline)

Цель: обеспечить однозначную связь **требование → работа → изменения → проверка → релиз**.

## 1) Идентификаторы

### Требования (Requirements Specification)
- `RS-A-XX` — требования Потока 1 (Telegram-консультант), источник: `official_requirements_specification.md`.
- `RS-B-XX` — требования Потока 2 (логистика), источник: `official_requirements_specification.md` (в рамках подготовки, без реализации в MVP).

### Решения/блокеры
- `D-XXX` — записи из `decision_log.md`.

### UAT
- `BOT-UAT-XX`, `CALC-UAT-XX`, `LOG-UAT-XX` — сценарии из `uat_acceptance_scenarios.md`.

### Работы (backlog)
- `WI-<AREA>-NNN` — work item (эпик/история/задача) из `management/backlog.md`.
  - `<AREA>`: `BASE`, `BOT`, `CALC`, `ADMIN`, `DATA`, `QA`, `REL`.

## 2) Правила ссылок

Каждый work item обязан содержать:
- ссылки на `RS-*` и/или `D-*`;
- список UAT сценариев (`BOT-UAT-*`, `CALC-UAT-*`) которые подтверждают результат;
- ожидаемые изменения (код/документы) и проверку (команды/артефакты).

## 3) Правила релиза

Релизная фиксация включает:
- версию формулы и источников (`calculator_formula_specification.md`, `decision_log.md`);
- утвержденный список UAT и результат (`uat_acceptance_scenarios.md` + протокол);
- релиз-ноты с перечнем work items и ссылками на проверки (`management/release_notes_v1.md`).

