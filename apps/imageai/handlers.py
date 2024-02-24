from bot import dp, bot, types
from .generate import LexicaAi
from filters.core import IsPrivate
from utils import text, constants
from utils.translate import translateMessage
from apps.subscription.managers import LimitManager
from apps.core.models import ChatActivity
from apps.subscription.managers import SubscriptionManager


dp.filters_factory.bind(IsPrivate)


async def isPermitted(chatId, message):
    if chatId == constants.HOST_GROUP_ID:
        await message.answer(text.IMAGE_GEN_NOT_AVAILABLE)
        return False

    if not LimitManager.checkImageaiRequestsDailyLimit(message.chat.id):
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

    images = await LexicaAi.generate(message.chat.id, query)
    images = LexicaAi.getRandomImages(images, 6)

    chatActivity = ChatActivity.getOrCreate(message.chat.id)
    ChatActivity.update(chatActivity, "todaysImages", chatActivity.todaysImages + 1)

    media_group = [types.InputMediaPhoto(media=url) for url in images]
    media_group[0].caption = f"\n🌄 {message.text}\n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sentMessage.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)
