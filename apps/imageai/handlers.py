from bot import dp, bot, types
from .generate import LexicaAi
from .keyboards import buyCreditMenu
from filters import IsPrivate

dp.filters_factory.bind(IsPrivate)


@dp.message_handler(commands=["art"], is_private=True)
async def handle_art(message: types.Message):
    query = message.get_args()

    if not query:
        return await message.answer("Iltimos so'rovingizni kiriting:\n` /art prompt` ", parse_mode="MARKDOWN")
    

    sent_message = await bot.send_message(message.chat.id, "...")

    await message.answer_chat_action("typing")

    images = LexicaAi.generate(query)

    images = LexicaAi.get_random_images(images, 6)

    media_group = [types.InputMediaPhoto(media=url) for url in images]

    media_group[0].caption = f"\n🌄 {query}\n\n<b>Ishlatilindi:</b> 20 aqsha\n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sent_message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)


