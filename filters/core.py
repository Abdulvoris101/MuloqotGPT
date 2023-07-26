from db.setup import session
from apps.core.models import Chat
import os
from app import bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from apps.core.keyboards import joinChannelMenu
from apps.core.managers import ChatManager


class UserFilter:

    @classmethod
    async def is_active(cls, chat_id):
        chat = Chat.get(chat_id)

        if chat is None:
            return False

        return chat.is_activated
    
    @classmethod
    async def is_subscribed(cls, chat_type, user_id):
        if chat_type == 'private':
            channel_id = os.environ.get("CHANNEL_ID")

            chat_member = await bot.get_chat_member(channel_id, user_id)

            if chat_member.is_chat_member():
                return True

            return False

        return True

    
    @classmethod
    async def activate_and_check(cls, message, chat_id):
        if not await cls.is_active(chat_id):
            await ChatManager.activate(message)
        elif not await cls.is_subscribed(message.chat.type, chat_id):
            return await message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)
