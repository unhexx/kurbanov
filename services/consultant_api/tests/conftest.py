import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:////tmp/consultant_api_test.db")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "")
os.environ.setdefault("TELEGRAM_WEBHOOK_SECRET_TOKEN", "")
os.environ.setdefault("TELEGRAM_MANAGER_CHAT_ID", "")
os.environ.setdefault("ADMIN_API_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
