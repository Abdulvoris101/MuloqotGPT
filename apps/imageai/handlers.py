from bot import dp, bot, types
from utils.requests import LexicaAi
from .keyboards import buyCreditMenu
from filters.imageai import IsPrivate
from apps.core.manager import Credit

dp.filters_factory.bind(IsPrivate)


@dp.message_handler(commands=["art"], is_private=True)
async def handle_art(message: types.Message):
    query = message.get_args()

    credit = Credit(message.from_user.id)

    if not query:
        return await message.answer("Iltimos so'rovingizni kiriting:\n` /art prompt` ", parse_mode="MARKDOWN")
    
    is_enough = credit.use(20)

    if not is_enough:
        return await message.answer("Sizda aqsha qolmadi ❌", reply_markup=buyCreditMenu)
    
    sent_message = await bot.send_message(message.chat.id, "...")

    await message.answer_chat_action("typing")

    
    images = LexicaAi.generate(query)

    images = LexicaAi.get_random_images(images, 6)

    media_group = [types.InputMediaPhoto(media=url) for url in images]

    media_group[0].caption = f"\n🌄 {query}\n\n<b>Ishlatilindi:</b> 20 aqsha\n<b>Balans:</b> {credit.get()[0]} aqsha \n\n@muloqataibot"
    
    await bot.delete_message(message.chat.id, message_id=sent_message.message_id)
    await bot.send_media_group(message.chat.id, media=media_group)

