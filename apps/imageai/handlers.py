from bot import dp, bot, types
from .generate import LexicaAi
from filters.core import IsPrivate
from utils import text, constants
from utils.translate import translateMessage
from apps.subscription.managers import LimitManager
from apps.core.models import ChatActivity
from apps.subscription.managers import SubscriptionManager


dp.filters_factory.bind(IsPrivate)


async def handleArt(message: types.Message):
    userChat = message.chat

    query = translateMessage(message.text,
                             chatId=userChat.id,
                             from_="auto",
                             lang="en",
                             is_translate=True)
    
    if userChat.id == constants.HOST_GROUP_ID:
        return await message.answer("Bu guruhda rasm generatsiya qilib bo'lmaydi!")
    
    if not LimitManager.checkImageaiRequestsDailyLimit(message.chat.id):
        if userChat.id == constants.IMAGE_GEN_GROUP_ID:
            return await message.answer(text.LIMIT_GROUP_REACHED)

        return await message.answer(text.getLimitReached(SubscriptionManager.isPremiumToken(userChat.id)))

    sent_message = await bot.send_message(message.chat.id, "⏳")
    await message.answer_chat_action("typing")

    images = await LexicaAi.generate(message.chat.id, query)

    chatActivity = ChatActivity.get(message.chat.id)
    
    if chatActivity is None:
        ChatActivity(chatId=message.chat.id).save()
        chatActivity = ChatActivity.get(message.chat.id)
    
    ChatActivity.update(chatActivity, "todaysImages", chatActivity.todaysImages + 1)

    images = LexicaAi.getRandomImages(images, 6)

    media_group = [types.InputMediaPhoto(media=url) for url in images]

    media_group[0].caption = f"\n🌄 {message.text}\n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sent_message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)