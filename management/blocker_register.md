# Blocker register — MVP (Поток 1) / Deferred (Поток 2)

Реестр предназначен для фиксации **открытых вопросов и блокеров**, которые влияют на scope/приемку/качество/сроки.  
Где применимо, записи ссылаются на решения `D-*` из `decision_log.md` и источники корпуса KB `KB-SRC-*` из `knowledge_base_corpus_register.md`.

| ID | Type | Description | Impact | Owner | Status | Affected WI stories | Source link |
|---|---|---|---|---|---|---|---|
| BR-001 | Blocker | Материалы заказчика для KB: внутренний FAQ (KB-SRC-08) — не предоставлен/не промодерирован. | Quality: снижение покрытия ответов, рост эскалаций (BOT-UAT-07). | Заказчик, Дмитрий | waiting_customer | WI-ADMIN-030, WI-BOT-015 | KB-SRC-08, D-005 |
| BR-002 | Blocker | Материалы заказчика: обезличенные диалоги менеджеров (KB-SRC-09) — нет выгрузки/обезличивания/правил модерации. | Quality: словарь/сценарии не пополняются, рост unknown вопросов. | Заказчик, Дмитрий | waiting_customer | WI-ADMIN-030, WI-BOT-015 | KB-SRC-09 |
| BR-003 | Blocker | Требуется `TELEGRAM_BOT_TOKEN` для запуска/деплоя (создание бота и выдача токена). | Schedule: без токена невозможна интеграция с Telegram и UAT в боевом канале. | Заказчик, Дмитрий | waiting_customer | WI-BOT-002, WI-BOT-011..016 | `.env.example` |
| BR-004 | Open question | Политика webhook секретов: будет ли в stage/prod обязательный `TELEGRAM_WEBHOOK_SECRET_TOKEN` (и как он будет ротироваться)? | Quality/Security: риск подмены webhook при пустом секрете; влияет на эксплуатацию. | Руководитель разработки | open | WI-BOT-002 | `.env.example` |
| BR-005 | Open question | Нужен ли `TELEGRAM_MANAGER_CHAT_ID` в MVP для уведомлений менеджера об эскалациях (и какой чат/канал использовать)? | Scope/Quality: влияет на скорость реакции менеджера; без chat id возможно “тихое” накопление эскалаций. | Заказчик, Дмитрий | open | WI-BOT-012, WI-DATA-020 | `.env.example`, D-012 |
| BR-006 | Blocker | `ADMIN_API_TOKEN` обязателен для любых shared/stage/prod окружений (в dev допускается пустой). Кто генерирует/хранит/ротирует? | Security: без токена админ endpoints открыты (неприемлемо вне dev). | Руководитель разработки | open | WI-ADMIN-010..040 | `.env.example` |
| BR-007 | Deferred | Поток 2: перечень 15 логистических источников для заполнения API-матрицы отсутствует (ожидается от заказчика и Тамары). | Scope/Schedule: невозможно оценить/стартовать поток 2 без перечня источников. | Заказчик, Тамара | deferred | (Поток 2, вне MVP) | D-013, `logistics_api_matrix.md` |
| BR-008 | Deferred | Поток 2: подтверждение ToS/правовой допустимости API/parsing по источникам + выбор 2–4 источников первой очереди. | Scope/Cost/Schedule: без подтверждений нельзя включать в оценку/реализацию потока 2. | Тамара | deferred | (Поток 2, вне MVP) | D-014, D-015, `logistics_api_matrix.md` |

