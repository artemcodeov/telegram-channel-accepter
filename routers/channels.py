from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tools import bot, entities_convert
from db import get_all_channels, create_channel, session, get_channel
from schemas import AdminCallback, AdminChannelCallback

channels = Router()


class Channel(StatesGroup):
    id = State()
    name = State()
    welcome_text = State()


class WelcomeEdit(StatesGroup):
    id = State()
    welcome_text = State()


@channels.callback_query(AdminCallback.filter(F.location == "channel"),
                         AdminCallback.filter(F.action == "menu"))
async def admin_channel(query: types.CallbackQuery):
    all_channels = await get_all_channels()
    builder = InlineKeyboardBuilder()
    builder.button(text="Create channel", callback_data=AdminCallback(location="channel", action="create"))
    for channel in all_channels:
        builder.button(text=f"{channel.id}: {channel.name}",
                       callback_data=AdminChannelCallback(action="edit", channel_id=channel.channel_id))
    await bot.send_message(query.from_user.id, "Choose channel or create", reply_markup=builder.as_markup())


@channels.callback_query(AdminCallback.filter(F.location == "channel"),
                         AdminCallback.filter(F.action == "create"))
async def admin_create_channel(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Channel.id)
    await bot.send_message(query.from_user.id, "Type channel ID (e.g. -100004343)")


# TODO: Add validators to processors

@channels.message(Channel.id)
async def process_channel_id(msg: types.Message, state: FSMContext):
    await state.update_data(id=msg.text)
    await state.set_state(Channel.name)
    await bot.send_message(msg.from_user.id, "Type channel human-readable name (e.g. My Channel)")


@channels.message(Channel.name)
async def process_channel_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(Channel.welcome_text)
    await bot.send_message(msg.from_user.id, "Ok, now type welcome text (Text that sends to accepted user by this bot)")


@channels.message(Channel.welcome_text)
async def process_channel_welcome_text(msg: types.Message, state: FSMContext):
    await state.update_data(welcome_text=msg.text)
    data = await state.get_data()
    await create_channel(data['id'], data['name'], data['welcome_text'])
    await state.clear()
    await bot.send_message(msg.from_user.id, "Successful! Channel added")


@channels.callback_query(AdminChannelCallback.filter(F.action == "edit"))
async def edit_channel(query: types.CallbackQuery, callback_data: AdminChannelCallback):
    builder = InlineKeyboardBuilder()
    builder.button(text="Edit welcome text",
                   callback_data=AdminChannelCallback(action="edit_welcome", channel_id=callback_data.channel_id))
    await bot.send_message(query.from_user.id, "What do you want to do?", reply_markup=builder.as_markup())


@channels.callback_query(AdminChannelCallback.filter(F.action == "edit_welcome"))
async def edit_welcome(query: types.CallbackQuery, callback_data: AdminChannelCallback, state: FSMContext):
    await state.set_state(WelcomeEdit.welcome_text)
    await state.update_data(id=callback_data.channel_id)
    await bot.send_message(query.from_user.id, "Type welcome text")


@channels.message(WelcomeEdit.welcome_text)
async def process_edit_welcome_text(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    channel = await get_channel(data['id'])
    async with session() as s:
        channel.welcome_text = entities_convert(msg)
        s.add(channel)
        await s.commit()
    await bot.send_message(msg.from_user.id, "Successful!")
