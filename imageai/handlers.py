from bot import dp, bot, types
from .utils import LexicaAi 
from .keyboards import refreshMenu
from aiogram.dispatcher.filters import Command
from .filters import IsPrivate


dp.filters_factory.bind(IsPrivate)

@dp.message_handler(commands=["art"], is_private=True)
async def handle_art(message: types.Message):
    query = message.get_args()
    
    if not query:
        return await message.answer("Iltimos so'rovingizni kiriting:\n` /art prompt` ", parse_mode="MARKDOWN")
    
    message = await bot.send_message(message.chat.id, "...")

    images = LexicaAi.generate(query)

    images = LexicaAi.get_random_images(images, 6)

    media_group = [types.InputMediaPhoto(media=url) for url in images]

    media_group[0].caption = f"\n🌄 <b>{query}</b>\n\n@muloqataibot"

    await bot.delete_message(message.chat.id, message_id=message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)

