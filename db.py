from typing import Union, Optional, AsyncGenerator, List
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import schemas
from models import User, Channel
from settings import DATABASE_URL

database_url = DATABASE_URL
if DATABASE_URL.startswith("sqlite"):
    first_part, second_part = DATABASE_URL.split(":")
    first_part += "+aiosqlite"
    database_url = first_part + second_part
elif DATABASE_URL.startswith("postgres"):
    first_part, second_part = DATABASE_URL.split(":")
    first_part += "+asyncpg"
    database_url = first_part.replace("postgres", "postgresql") + second_part
engine = create_async_engine(database_url)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_user(user_id: Union[int, types.Message, types.CallbackQuery]) -> schemas.User:
    if type(user_id) != int:
        user_id = user_id.from_user.id

    async with session() as s:
        result = await s.execute(select(User).where(User.user_id == user_id))
        return result.scalars().one_or_none()


async def get_all_users() -> List[schemas.User]:
    async with session() as s:
        result = await s.execute(select(User))
        return result.scalars().all()


async def get_channel(channel_id: Union[int, str, types.Message]) -> schemas.Channel:
    if type(channel_id) != int:
        channel_id = channel_id.chat.id
    elif type(channel_id) == str:
        channel_id = int(channel_id)

    async with session() as s:
        result = await s.execute(select(Channel).where(Channel.channel_id == channel_id))
        return result.scalars().one_or_none()


async def get_all_channels() -> List[schemas.Channel]:
    async with session() as s:
        result = await s.execute(select(Channel))
        return result.scalars().all()


async def create_channel(channel_id: int, name: str, welcome_text: str) -> None:
    async with session() as s:
        channel = Channel(channel_id=channel_id, name=name, welcome_text=welcome_text)
        s.add(channel)
        await s.commit()


async def create_user(user: Union[types.User, schemas.TypeUser], channel: Union[int, Channel, None] = None) -> None:
    async with session() as s:
        user = User(user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    channel=channel)
        s.add(user)
        await s.commit()


async def create_or_get_user(user: Union[types.User, schemas.TypeUser],
                        channel: Union[int, Channel, None] = None) -> Optional[schemas.User]:
    if isinstance(user, types.User):
        user = await get_user(user.id)
    else:
        user = await get_user(user.user_id)
    if user:
        return user
    else:
        await create_user(user, channel)
