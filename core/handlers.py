from app import dp, bot, types, AdminLoginState
from db.manager import Group, Message, Admin
from aiogram.dispatcher.filters import BoundFilter
from .utils import translate_message, translate_response
from main import answer_ai
from aiogram.dispatcher.filters import Command
import sys

async def handle_ai_message(message):
    group_chat = Group(message.chat.id, message.chat.full_name)
    ru_message = translate_message(message.text, lang='ru')

    message_obj = Message(message=ru_message, chat_id=message.chat.id)
    messages = message_obj.get_messages()
    
    if not group_chat.is_active():
        return await message.answer("Muloqotni boshlash uchun - /startai")
    
    elif len(messages) <= 2 and message.chat.type != 'private':
        messages.append({'role': 'user', 'content': ru_message + '😂'})
    else:
        messages.append({'role': 'user', 'content': ru_message, "dsa": "Dsa"})
    

    response = answer_ai(messages, chat_id=message.chat.id)


    response_uz = translate_response(response)

    await message.reply(response_uz)


    message_obj.create_message(role='user', message=ru_message, uz_message=message.text)
    message_obj.create_message(role='assistant', message=response, uz_message=response_uz)

    messages.pop()


@dp.message_handler(lambda message: not message.text.startswith('/') and message.chat.type == 'private')
async def handle_messages(message: types.Message,):
    return await handle_ai_message(message)
    

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):

    await message.answer(""" 🤖 Salom! Men MuloqotAi, sizning shaxsiy AI yordamchingizman, sizga qiziqarli va ulashingizga imkon beradigan suhbat tajribasi taqdim etish uchun yaratilganman 😉. Ochiq guruh - @muloqataigr""")

    await message.answer("""Endi muloqotai guruhda xam ishlaydi - /groupinfo.
Meni boshqa chatbotlardan farq qilishim - /me !    
Batafsil ma'lumot uchun - /help""")



@dp.message_handler(commands=['groupinfo'])
async def group_info(message: types.Message):
    await message.answer("""Men endi guruhlar bilan ham ishlash imkoniyatiga egaman. Bu sizning guruhingizdagi a'zolar bilan birga muloqot qilishim va ularning savollari va talablari bo'yicha yordam berish imkonini beradi. Men bilan suxbat olib borish uchun shunchaki mening xabarimga reply qiling.
Shuningdek, Men guruh bilan hazil va latifalar bilan gaplashish imkoniyatiga egaman.""")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):

    await message.answer("""Shaxsiy va guruh suhbatlaringizda yordam beradigan foydali  yordamchi! Ushbu botning guruhda ishlash tartibi quyidagicha:

1️⃣ <b>Guruhga qo'shish</b>: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@muloqataibot" ni qidiring va uningni gruhga taklif qiling.

2️⃣ <b>Admin huquqlarini berish</b>: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.

3️⃣ <b>Gruhda suhbatlashish</b>: MuloqotAI gruhda /startai kommandasini kiritsangiz  bot faol bo'ladi va u bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Guruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin. Agarda vaqtinchalik to'xtatib turmoqchi bo'lsangiz /stopai kommandasini yuboring. 

➕ <b>Qo'shimcha</b>: Xabarlarni botning lichkasida xam yubora olasiz

""")


@dp.message_handler(commands=['me'])
async def me(message: types.Message):

    await message.answer(""" 💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, sizga aniqligi va maqbul javoblarni taklif etishim mumkin.

🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.

😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim! """)



@dp.message_handler(commands=['startai'])
async def activate(message: types.Message):
    group_chat = Group(message.chat.id, message.chat.full_name)

    group_chat.activate_group(str(message.chat.type))

    await message.reply("MuloqotAi hozir faol holatda va sizga yordam berishga tayyor!")


@dp.message_handler(commands=['stopai'])
async def deactivate(message: types.Message):
    group_chat = Group(message.chat.id, message.chat.full_name)

    group_chat.deactivate_group()

    await message.reply("MuloqotAi toxtatilindi. Muloqotni boshlash uchun - /startai")
    

class IsReplyFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.reply_to_message is not None


@dp.message_handler(IsReplyFilter())
async def handle_reply(message: types.Message):

    return await handle_ai_message(message)
    
