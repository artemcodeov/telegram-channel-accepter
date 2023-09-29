from typing import Optional, Union

from aiogram.filters.callback_data import CallbackData
from pydantic import BaseModel

import models


class TypeChannel(BaseModel):
    id: int
    name: str
    channel_id: int
    welcome_text: str
    welcome_photo: Optional[str]


class TypeUser(BaseModel):
    id: Optional[int] = None
    user_id: int
    first_name: str = ""
    last_name: Optional[str] = None
    username: Optional[str] = None
    admin: bool = False
    channel: Optional[int] = None
    banned_bot: bool = False


User = Union[TypeUser, models.User]
Channel = Union[TypeChannel, models.Channel]


class AdminCallback(CallbackData, prefix="admin"):
    location: str
    action: str


class AdminChannelCallback(CallbackData, prefix="channel"):
    action: str
    channel_id: int
