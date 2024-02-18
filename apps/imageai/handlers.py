from bot import dp, bot, types
from .generate import LexicaAi
from filters import IsPrivate
from utils import text, constants
from utils.translate import translate_message
from apps.subscription.managers import LimitManager
from apps.core.models import ChatActivity



dp.filters_factory.bind(IsPrivate)

def isChatAllowed(chatType, chatId):
    
    if chatType in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
        if int(chatId) != int(constants.HOST_GROUP_ID):
            return False

    return True


async def handleArt(message: types.Message):
    query = translate_message(message.text, message.chat.id, from_="auto", lang="en", is_translate=True)
    
    if isChatAllowed(message.chat.type, message.chat.id) == False:
        return await message.answer("Afsuski xozirda bot @muloqotaigr dan boshqa  guruhlarni qo'llab quvatlamaydi!")
            
    if message.chat.id == constants.HOST_GROUP_ID:
        return await message.answer("Bu guruhda rasm generatsiya qilib bo'lmaydi!")
    
    if not LimitManager.checkImageaiRequestsDailyLimit(message.chat.id):
        if message.chat.id == constants.HOST_GROUP_ID:
            return await message.answer(text.LIMIT_GROUP_REACHED)

        return await message.answer(text.LIMIT_REACHED)

    sent_message = await bot.send_message(message.chat.id, "...")

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