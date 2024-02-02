from bot import dp, bot, types
from .generate import LexicaAi
from filters import IsPrivate
from utils import text, constants
from apps.subscription.managers import LimitManager
from apps.core.models import ChatActivity


dp.filters_factory.bind(IsPrivate)

def isChatAllowed(chatType, chatId):
    
    if chatType in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
        if chatId != constants.HOST_GROUP_ID:
            return False

    return True


@dp.message_handler(commands=["art"])
async def handleArt(message: types.Message):
    query = message.get_args()
    
    if isChatAllowed(message.chat.type, message.chat.id) == False:
        return await message.answer("Afsuski xozirda bot @muloqotaigr dan boshqa  guruhlarni qo'llab quvatlamaydi!")
        
    if not query:
        return await message.answer("Iltimos so'rovingizni kiriting:\n` /art prompt` ", parse_mode="MARKDOWN")
    
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

    media_group[0].caption = f"\n🌄 {query}\n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sent_message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)