import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST_URL = os.getenv("HOST_URL")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = HOST_URL + WEBHOOK_PATH

DATABASE_URL = os.getenv("DATABASE_URL")
