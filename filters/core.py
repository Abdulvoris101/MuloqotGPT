from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from utils import containsAnyWord, constants


class isBotMentioned(BoundFilter):
    async def check(self, message: types.Message) -> bool:

        if not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅'):

            if message.reply_to_message is not None:
                if message.reply_to_message.from_user.is_bot:
                    return True

            message = str(message.text).lower()

            allowedTexts = ["muloqotai", "@muloqataibot", "generate", "imagine", "bot"]

            return containsAnyWord(message, allowedTexts)

def isGroupAllowed(
    chatType,
    chatId
):
    if chatType in constants.AVAILABLE_GROUP_TYPES:
        if int(chatId) not in constants.ALLOWED_GROUPS:
            return False
    return True
