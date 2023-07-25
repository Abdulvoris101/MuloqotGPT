from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

class IsPrivate(BoundFilter):
    key = 'is_private'

    
    def __init__(self, is_private):
        self.is_private = is_private

    async def check(self, message: types.Message) -> bool:
        return message.chat.type == 'private'