"""Конфигурация бота — читает переменные окружения."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
SITE_URL = os.getenv("SITE_URL", "https://itradebot.netlify.app")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Ivanov_sam")
DB_PATH = Path(__file__).parent / "itradebot.db"

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN не найден")
if not ADMIN_ID:
    raise SystemExit("❌ ADMIN_ID не найден")