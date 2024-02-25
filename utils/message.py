import asyncio
from aiogram.utils.exceptions import BotBlocked
from apps.core.managers import ChatManager
from apps.subscription.managers import PlanManager
from bot import bot


async def sendAnyMessages(users, message, inlineKeyboards=None):
    sendAny = SendAny(message)

    async def process_user(user):
        try:
            contentTypeHandlers = {
                "text": sendAny.sendMessage,
                "photo": sendAny.sendPhoto,
                "video": sendAny.sendVideo,
                "animation": sendAny.sendAnimation
            }

            content_type = message.content_type
            handler = contentTypeHandlers.get(content_type)

            if handler:
                await handler(chatId=user.chatId, kb=inlineKeyboards)

        except Exception as e:
            return 0

    tasks = [process_user(user) for user in users]
    blockedUsersCount = await asyncio.gather(*tasks)

    return blockedUsersCount


class SendAny:
    def __init__(self, message):
        self.message = message

    async def sendPhoto(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption)
            else:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption, reply_markup=kb)
        except BotBlocked:
            pass

    async def sendMessage(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_message(chatId, self.message.text)
            else:
                await bot.send_message(chatId, self.message.text, reply_markup=kb)
        except BotBlocked:
            pass

    async def sendVideo(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption)
            else:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption,
                                     reply_markup=kb)
        except BotBlocked:
            pass

    async def sendAnimation(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_animation(chatId, animation=self.message.animation.file_id, caption=self.message.caption)
            else:
                await bot.send_animation(chatId, animation=self.message.animation.file_id, caption=self.message.caption,
                                         reply_markup=kb)
        except BotBlocked:
            pass


def fetchUsersByType(contentType):
    if contentType == "FREE":
        users = PlanManager.getFreePlanUsers()
    elif contentType == "ALL":
        users = ChatManager.all()
    else:
        return False

    return users

