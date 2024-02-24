from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from utils import containsAnyWord, constants
from apps.admin.models import Admin


class isBotMentioned(BoundFilter):
    async def check(self, message: types.Message) -> bool:

        if not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅'):

            if message.reply_to_message is not None:
                if message.reply_to_message.from_user.is_bot:
                    return True

            message = str(message.text).lower()

            allowedTexts = ["muloqotai", "@muloqataibot", "generate", "imagine", "bot"]

            return containsAnyWord(message, allowedTexts)


class IsPrivate(BoundFilter):
    key = 'is_private'

    def __init__(self, is_private):
        self.is_private = is_private

    async def check(self, message: types.Message) -> bool:
        return message.chat.type == 'private'


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return Admin.isAdmin(userId=message.from_user.id)


class IsReplyFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.is_bot:
                return True

        return  str(message.text).lower().startswith("muloqotai") or str(message.text).lower().startswith("@muloqataibot")


def isGroupAllowed(
    chatType,
    chatId
):
    if chatType in constants.AVAILABLE_GROUP_TYPES:
        if int(chatId) not in constants.ALLOWED_GROUPS:
            return False
    return True


def checkPassword(password):
    if password == str(constants.PASSWORD):
        return True

    return False
