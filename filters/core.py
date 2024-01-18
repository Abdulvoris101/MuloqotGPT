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
    async def isActive(cls, chatId):
        chat = Chat.get(chatId)

        if chat is None:
            return False

        return chat.isActivated
    

    
    @classmethod
    async def activate(cls, message, chatId):
        if not await cls.isActive(chatId):
            await ChatManager.activate(message)
        