from apps.common.settings import settings
from bot import bot
from utils import text, countTokenOfMessage
from aiogram import types


def isGroupAllowed(
    chatType: str,
    chatId: int,
) -> bool:
    if chatType in settings.AVAILABLE_GROUP_TYPES:
        if chatId not in settings.ALLOWED_GROUPS:
            return False

    return True


def checkPassword(password) -> bool:
    if password == settings.PASSWORD:
        return True
    return False


async def isChatMember(userId: int):
    chatMember = await bot.get_chat_member(settings.REQUIRED_CHANNEL_ID, userId)

    if chatMember.status in ["member", "administrator", "creator"]:
        return True

    return False
