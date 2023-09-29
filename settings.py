import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST_URL = os.getenv("HOST_URL", "http://localhost:8000")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = HOST_URL + WEBHOOK_PATH

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "makemeadmin")

BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = "/media/"

if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)
