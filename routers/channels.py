from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import MEDIA_ROOT
from tools import bot, entities_convert, download_image
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


class RemoveState(StatesGroup):
    are_you_sure = State()


class RemoveChannelCallback(CallbackData, prefix="remove_channel"):
    answer: bool


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
    await bot.send_message(query.from_user.id, "Type channel ID (e.g. -100004343) or just forward any message")


# TODO: Add validators to processors

@channels.message(Channel.id)
async def process_channel_id(msg: types.Message, state: FSMContext):
    if msg.forward_from:
        await state.update_data(id=msg.forward_from.id)
    else:
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
    data = await state.get_data()
    text = entities_convert(msg)
    if msg.content_type == ContentType.PHOTO:
        filepath = await download_image(msg)
        await create_channel(data['id'], data['name'], text, filepath)
    elif msg.content_type == ContentType.TEXT:
        await create_channel(data['id'], data['name'], text)
    await state.clear()
    await bot.send_message(msg.from_user.id, "Successful! Channel added")


@channels.callback_query(AdminChannelCallback.filter(F.action == "edit"))
async def edit_channel(query: types.CallbackQuery, callback_data: AdminChannelCallback):
    builder = InlineKeyboardBuilder()
    builder.button(text="Edit welcome text",
                   callback_data=AdminChannelCallback(action="edit_welcome", channel_id=callback_data.channel_id))
    builder.button(text="Remove channel",
                   callback_data=AdminChannelCallback(action="remove_channel", channel_id=callback_data.channel_id))
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
    text = entities_convert(msg)
    async with session() as s:
        if msg.content_type == ContentType.PHOTO:
            filepath = await download_image(msg)
            channel.welcome_text = text
            channel.welcome_photo = filepath
        elif msg.content_type == ContentType.TEXT:
            channel.welcome_text = text
            channel.welcome_photo = None
        s.add(channel)
        await s.commit()
    await bot.send_message(msg.from_user.id, "Successful!")


@channels.callback_query(AdminChannelCallback.filter(F.action == "remove_channel"))
async def remove_channel(query: types.CallbackQuery, callback_data: AdminChannelCallback, state: FSMContext):
    await state.set_state(RemoveState.are_you_sure)
    await state.update_data(id=callback_data.channel_id)
    builder = InlineKeyboardBuilder()
    builder.button(text="Yes", callback_data=RemoveChannelCallback(answer=True))
    builder.button(text="No", callback_data=RemoveChannelCallback(answer=False))
    await bot.send_message(query.from_user.id, "Are you sure?", reply_markup=builder.as_markup())


@channels.callback_query(RemoveState.are_you_sure)
async def process_remove_channel(query: types.CallbackQuery, callback_data: RemoveChannelCallback, state: FSMContext):
    data = await state.get_data()
    if callback_data.answer is True:
        channel = await get_channel(data['id'])
        async with session() as s:
            s.delete(channel)
            await s.commit()
    await bot.send_message(query.from_user.id, "OK")
    await state.clear()
