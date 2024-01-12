from bot import dp, bot, types
from .generate import LexicaAi
from filters import IsPrivate
from utils import text
from apps.subscription.managers import SubscriptionManager
from apps.core.models import MessageStats

dp.filters_factory.bind(IsPrivate)



@dp.message_handler(commands=["art"], is_private=True)
async def handle_art(message: types.Message):
    query = message.get_args()

    if not query:
        return await message.answer("Iltimos so'rovingizni kiriting:\n` /art prompt` ", parse_mode="MARKDOWN")
    
    if not SubscriptionManager.check_imageai_requests_daily_limit(message.from_user.id):
        return await message.answer(text.LIMIT_REACHED)

    sent_message = await bot.send_message(message.chat.id, "...")

    await message.answer_chat_action("typing")

    images = LexicaAi.generate(query)

    messageStat = MessageStats.get(message.chat.id)

    MessageStats.update(messageStat, "todays_images", messageStat.todays_images + 1)

    images = LexicaAi.get_random_images(images, 6)

    media_group = [types.InputMediaPhoto(media=url) for url in images]

    media_group[0].caption = f"\n🌄 {query}\n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sent_message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)


