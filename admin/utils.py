from bot import bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from .models import Admin

class SendAny:
    def __init__(self, message):
        self.message = message
    
    async def send_photo(self, chat_id):
        await bot.send_photo(chat_id, self.message.photo[-1].file_id, caption=self.message.caption)
    
    async def send_message(self, chat_id):
        await bot.send_message(chat_id, self.message.text)

    async def send_video(self, chat_id):
        await bot.send_video(chat_id, video=self.message.video.file_id, caption=self.message.caption)


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return  Admin.is_admin(user_id=message.from_user.id)
