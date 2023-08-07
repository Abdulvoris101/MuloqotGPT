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
    async def activate(cls, message, chat_id):
        if not await cls.is_active(chat_id):
            await ChatManager.activate(message)
        