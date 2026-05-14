# MVP Telegram-консультанта (Поток 1) и подготовка Потока 2

Репозиторий содержит:
- baseline предпроектных документов (в корне репозитория);
- исходный код MVP (директория `services/consultant_api`);
- управленческие артефакты (директория `management`).

## Быстрый старт (локально)

### 1) Переменные окружения

Создайте `.env` по образцу:
```bash
cp .env.example .env
```

### 2) Поднять PostgreSQL
```bash
docker compose up -d db
```

### Альтернатива: поднять DB + API через Docker
```bash
docker compose up -d db api
docker compose exec api python scripts/init_db.py
docker compose exec api python scripts/seed.py
```

### 3) Установить зависимости и запустить API
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r services/consultant_api/requirements.txt
uvicorn app.main:app --app-dir services/consultant_api --reload
```

API поднимется на `http://localhost:8000`, swagger: `http://localhost:8000/docs`.

### 4) Инициализация БД (первый запуск)
```bash
python services/consultant_api/scripts/init_db.py
python services/consultant_api/scripts/seed.py
```

## Валидация
```bash
pip install -r services/consultant_api/requirements-dev.txt
pytest -q
```
