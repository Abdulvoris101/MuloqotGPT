class AiogramException(Exception):
    def __init__(self, userId, message_text, original_exception=None):
        self.userId = userId
        self.message_text = message_text
        self.original_exception = original_exception
