from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from apps.admin.models import Admin


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
