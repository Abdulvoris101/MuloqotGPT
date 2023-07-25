from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from apps.admin.models import Admin


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return  Admin.is_admin(user_id=message.from_user.id)
