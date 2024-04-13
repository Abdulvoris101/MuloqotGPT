from utils import constants


def isGroupAllowed(
    chatType,
    chatId,
    requestType="GPT"
) -> bool:
    if chatType in constants.AVAILABLE_GROUP_TYPES:
        if int(chatId) not in constants.ALLOWED_GROUPS:
            return False
        if requestType == "IMAGE" and chatId != constants.IMAGE_GEN_GROUP_ID:
            return False

    return True


def checkPassword(password) -> bool:
    if password == str(constants.PASSWORD):
        return True

    return False
