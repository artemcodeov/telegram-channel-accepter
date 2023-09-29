from aiogram import types, Dispatcher
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from bot import bot, dp
from settings import WEBHOOK_PATH, WEBHOOK_URL

app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def webhook_handler(update: dict):
    telegram_update = types.Update.model_validate(update, context={"bot": bot})
    await dp.feed_update(bot, telegram_update)
