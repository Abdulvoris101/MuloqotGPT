from aiogram import types
from aiogram.filters import Filter

from utils import containsAnyWord
from apps.admin.models import Admin


class isBotMentioned(Filter):
    async def __call__(self, message: types.Message) -> bool:

        if message.text.startswith('/'):
            return False

        if message.reply_to_message is not None and message.reply_to_message.from_user.is_bot:
            return True

        message = str(message.text).lower()
        allowedTexts = ["muloqotai", "@muloqataibot", "generate", "imagine", "bot"]
        return containsAnyWord(message, allowedTexts)


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return Admin.isAdmin(userId=message.from_user.id)