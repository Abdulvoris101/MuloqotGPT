from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Filter

from bot import logger
from utils import containsAnyWord
from apps.admin.models import Admin


class isBotMentioned(Filter):
    async def __call__(self, message: types.Message) -> bool:
        logger.debug("Checking message")

        if message.content_type != ContentType.TEXT:
            return False

        if message.text.startswith('/'):
            return False

        if message.reply_to_message is not None and message.reply_to_message.from_user.is_bot:
            return True

        message = str(message.text).lower()
        allowedTexts = ["muloqotgpt", "muloqot", "@muloqotgpt_bot", "@muloqotgpt", "generate", "imagine", "bot"]
        return containsAnyWord(message, allowedTexts)


class TextContentFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        if message.content_type != ContentType.TEXT:
            return False

        if message.text.startswith('/') or message.text == "Bekor qilish":
            return False

        return True


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return Admin.isAdmin(userId=message.from_user.id)