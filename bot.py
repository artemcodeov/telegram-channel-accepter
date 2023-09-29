import asyncio

from sqlalchemy import select

import models
from settings import SECRET_PASSWORD
from tools import bot
from aiogram import Dispatcher, types, F
from aiogram.filters import CommandStart
from db import get_user, get_channel, create_user, session, get_all_users
from routers.admin import admin

dp = Dispatcher()
dp.include_router(admin)


@dp.message(CommandStart())
async def start(message: types.Message):
    user = await get_user(message)
    if not user:
        await create_user(message.from_user)
    else:
        if user.banned_bot:
            async with session() as s:
                user.banned_bot = False
                s.add(user)
                await s.commit()
    # await message.answer(f"Salom, {message.from_user.full_name}")


@dp.message(F.text == SECRET_PASSWORD)
async def process_secret_password(msg: types.Message):
    async with session() as s:
        result = await s.execute(select(models.User).where(models.User.admin))
        if not result.scalars().all():
            user = await get_user(msg)
            user.admin = True
            s.add(user)
            await s.commit()
            await bot.send_message(msg.from_user.id, "You're now admin!")


@dp.chat_join_request()
async def join(update: types.ChatJoinRequest):
    user = await get_user(update.from_user.id)
    if not user:
        await create_user(update.from_user)
    channel = await get_channel(update.chat.id)
    await update.approve()
    await bot.send_message(update.from_user.id, channel.welcome_text)


async def polling() -> None:
    """Only for dev (before deploy on heroku etc.)"""
    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(polling())
