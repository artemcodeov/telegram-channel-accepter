from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import get_user, get_all_users, session
from routers.channels import channels
from routers.users import users
from schemas import AdminCallback
from tools import bot, entities_convert

admin = Router()
admin.include_router(channels)
admin.include_router(users)


class SpamState(StatesGroup):
    spam_text = State()


@admin.message(Command('admin'))
async def admin_command(msg: types.Message):
    user = await get_user(msg)
    if user.admin:
        builder = InlineKeyboardBuilder()
        builder.button(text="Channel", callback_data=AdminCallback(location="channel", action="menu"))
        builder.button(text="User", callback_data=AdminCallback(location="user", action="menu"))
        builder.button(text="Spam", callback_data=AdminCallback(location="spam", action="menu"))
        await msg.answer("Admin menu", reply_markup=builder.as_markup())
    else:
        await msg.answer("You are not admin")


@admin.callback_query(AdminCallback.filter(F.location == "spam"),
                      AdminCallback.filter(F.action == "menu"))
async def spam(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SpamState.spam_text)
    await bot.send_message(query.from_user.id, "Type message to spam or send photo")


@admin.message(SpamState.spam_text)
async def process_spam(msg: types.Message, state: FSMContext):
    await state.clear()
    text = entities_convert(msg)
    for user in await get_all_users():
        try:
            if msg.content_type == ContentType.PHOTO:
                await bot.send_photo(user.user_id, msg.photo[-1].file_id, caption=text)
            elif msg.content_type == ContentType.TEXT:
                await bot.send_message(user.user_id, text)
        except TelegramForbiddenError:
            async with session() as s:
                user.banned_bot = True
                s.add(user)
                await s.commit()
    await bot.send_message(msg.from_user.id, "Success!")
