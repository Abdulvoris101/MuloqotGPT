from aiogram import types
from aiogram.filters import Filter

from utils import containsAnyWord
from apps.admin.models import Admin



class isBotMentioned(Filter):
    async def __call__(self, message: types.Message) -> bool:

        if not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅'):

            if message.reply_to_message is not None:
                if message.reply_to_message.from_user.is_bot:
                    return True

            message = str(message.text).lower()

            allowedTexts = ["muloqotai", "@muloqataibot", "generate", "imagine", "bot"]

            return containsAnyWord(message, allowedTexts)


class IsPrivate(Filter):
    key = 'is_private'

    def __init__(self, is_private):
        self.is_private = is_private

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type == 'private'


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return Admin.isAdmin(userId=message.from_user.id)


class IsReplyFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.is_bot:
                return True

        return str(message.text).lower().startswith("muloqotai") or str(message.text).lower().startswith("@muloqataibot")

