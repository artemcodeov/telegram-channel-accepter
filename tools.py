from datetime import datetime

from aiogram import Bot, types
from aiogram.enums import ParseMode, ContentType

from entitiesconvert import MessageToHtmlConverter
from settings import BOT_TOKEN, MEDIA_ROOT


def entities_convert(msg: types.Message) -> str:
    if msg.content_type == ContentType.PHOTO:
        text = msg.caption
        if msg.entities:
            conv = MessageToHtmlConverter(text, msg.caption_entities)
            text = conv.html
        return text
    elif msg.content_type == ContentType.TEXT:
        text = msg.text
        if msg.entities:
            conv = MessageToHtmlConverter(text, msg.entities)
            text = conv.html
        return text


async def download_image(msg: types.Message):
    file = await bot.get_file(msg.photo[-1].file_id)
    ext = file.file_path.split(".")[-1]
    now = datetime.now()
    filename = now.strftime(f"photo_%d_%m_%Y_%H_%M.{ext}")
    await bot.download_file(file.file_path, MEDIA_ROOT / filename)
    return filename


bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
