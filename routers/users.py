from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import schemas
from db import create_user, get_user, session, create_or_get_user
from schemas import AdminCallback
from tools import bot

from aiogram.utils.keyboard import InlineKeyboardBuilder

users = Router()


class UserCallback(CallbackData, prefix="users"):
    action: str


class UserState(StatesGroup):
    user_id = State()


@users.callback_query(AdminCallback.filter(F.location == "user"),
                      AdminCallback.filter(F.action == "menu"))
async def user_menu(query: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="Make user Admin", callback_data=UserCallback(action="make_user_admin"))
    await bot.send_message(query.from_user.id, "What do you want to do?", reply_markup=builder.as_markup())


@users.callback_query(UserCallback.filter(F.action == "make_user_admin"))
async def make_user_admin(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.user_id)
    await bot.send_message(query.from_user.id, "Send me an ID of User (ex: 474504116) or forward me any his message")


@users.message(UserState.user_id)
async def process_user_id(msg: types.Message, state: FSMContext):
    if msg.forward_from:
        user_id = msg.forward_from.id
        await create_or_get_user(msg.forward_from)
    else:
        if msg.text.isdigit():
            user_id = int(msg.text)
            await create_or_get_user(schemas.TypeUser(user_id=user_id))
        else:
            await bot.send_message(msg.from_user.id, "Send me id, not string")
            return

    async with session() as s:
        user = await get_user(user_id)
        user.admin = True
        s.add(user)
        await s.commit()
        await state.clear()
        await bot.send_message(msg.from_user.id, "Successful!")

