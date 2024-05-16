from typing import Optional


class AiogramException(Exception):
    def __init__(self, userId, message_text, original_exception=None):
        self.userId = userId
        self.message_text = message_text
        self.original_exception = original_exception


class ForbiddenException(Exception):
    def __init__(self, chatId, messageText, original_exception=None):
        self.userId = chatId
        self.message_text = messageText
        self.original_exception = original_exception


class InvalidRequestException(Exception):
    def __init__(self, chatId: int, messageText: str, apikey: Optional[str] = '', exceptionText: str = ''):
        self.chatId = chatId
        self.messageText = messageText
        self.exceptionText = exceptionText
        self.apiKey = apikey
