from utils import constants


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
