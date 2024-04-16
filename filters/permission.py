from utils import constants, text, countTokenOfMessage
from aiogram import types


def isGroupAllowed(
    chatType: str,
    chatId: int,
) -> bool:
    if chatType in constants.AVAILABLE_GROUP_TYPES:
        if chatId not in constants.ALLOWED_GROUPS:
            return False

    return True


def checkPassword(password) -> bool:
    if password == constants.PASSWORD:
        return True
    return False
