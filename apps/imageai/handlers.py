from aiogram.utils.exceptions import BadRequest

from bot import dp, bot, types
from utils.events import sendError
from utils.exception import AiogramException
from .generate import LexicaAi
from filters.bound_filters import IsPrivate
from utils import text, constants
from utils.translate import translateMessage
from apps.subscription.managers import LimitManager
from apps.core.models import ChatActivity
from apps.subscription.managers import SubscriptionManager


dp.filters_factory.bind(IsPrivate)


async def isPermitted(chatId, message):
    if not LimitManager.checkRequestsDailyLimit(message.chat.id, messageType="IMAGE"):
        if chatId == constants.IMAGE_GEN_GROUP_ID:
            await message.answer(text.LIMIT_GROUP_REACHED)
            return False

        await message.answer(text.getLimitReached(SubscriptionManager.isPremiumToken(chatId)))
        return False

    return True


async def handleArt(message: types.Message):
    userChat = message.chat

    query = translateMessage(message.text,
                             from_="auto",
                             to="en",
                             isTranslate=True)

    if not await isPermitted(chatId=userChat.id, message=message):
        return

    sentMessage = await bot.send_message(message.chat.id, "⏳")
    await message.answer_chat_action("typing")

    try:
        images = await LexicaAi.generate(message.chat.id, query)
    except AiogramException as e:
        await bot.delete_message(userChat.id, message_id=sentMessage.message_id)
        await bot.send_message(userChat.id, e.message_text)
        return

    images = LexicaAi.getRandomImages(images, 6)

    chatActivity = ChatActivity.getOrCreate(message.chat.id)
    ChatActivity.update(chatActivity, "todaysImages", chatActivity.todaysImages + 1)

    media_group = [types.InputMediaPhoto(media=url) for url in images]
    media_group[0].caption = f"\n🌄 {message.text}\n\n@muloqataibot"
    
    await bot.delete_message(userChat.id, message_id=sentMessage.message_id)

    try:
        await bot.send_media_group(userChat.id, media=media_group)
    except BadRequest as e:
        await bot.send_message(userChat.id, "Rasm generatsiya qilishda xatolik. Iltimos boshqatan so'rov yuboring!")