from aiogram import Bot, types
from aiogram.enums import ParseMode

from entitiesconvert import MessageToHtmlConverter
from settings import BOT_TOKEN


def entities_convert(msg: types.Message) -> str:
    text = msg.text
    if msg.entities:
        conv = MessageToHtmlConverter(text, msg.entities)
        text = conv.html
    return text


bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
