from app import dp, bot, types
from db.manager import Group, Message
from aiogram.dispatcher.filters import BoundFilter
from .utils import translate_message
from main import answer_ai

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(""" 🤖 Salom! Men MuloqotAi, sizning shaxsiy AI yordamchingizman, sizga qiziqarli va ulashingizga imkon beradigan suhbat tajribasi taqdim etish uchun yaratilganman. Meni boshqa chatbotlardan farq qilishim - /me !.
Batafsil ma'lumot uchun - /help""")



@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(""" Guruh suhbatlaringizda yordam beradigan foydali  yordamchi! Ushbu botning ishlash tartibi quyidagicha:

1️⃣ Gruhga qo'shish: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@MuloqotAibot" ni qidiring va uningni gruhga taklif qiling.

2️⃣ Admin huquqlarini berish: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.

3️⃣ Gruhda suhbatlashish: MuloqotAI gruhda /startai kommandasini kiritsangiz  bot faol bo'ladi va u bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Gruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin. Agarda vaqtinchalik to'xtatib turmoqchi bo'lsangiz /stopai kommandasini yuboring. 

4️⃣ Aqlli javoblar: MuloqotAI g'oya muhandisligidan foydalanib gruh suhbatlarining mazmunini tushunadi. U foydali javoblar berish, manfaatli muloqotlarni olib borish, takliflarni taklif etish va latifalar bilan shug'ullanishga imkon beradi.

""")


@dp.message_handler(commands=['me'])
async def me(message: types.Message):
    await message.answer(""" 💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, sizga aniqligi va maqbul javoblarni taklif etishim mumkin.

🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.

😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim! """)



@dp.message_handler(commands=['startai'])
async def activate(message: types.Message):
    group_chat = Group(message.chat.id, message.chat.full_name)

    group_chat.activate_group()

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
    group_chat = Group(message.chat.id, message.chat.full_name)
    ru_message = translate_message(message.text)
    message_obj = Message(message=ru_message, chat_id=message.chat.id)
    messages = message_obj.get_messages()
    
    
    if not group_chat.is_active():
        return await message.answer("MuloqotAi toxtatilingan. Muloqotni qayta boshlash uchun - /startai")
    

    messages.append({'role': 'user', 'content': ru_message})

    response = answer_ai(messages)

    await message.reply(response)

    message_obj.create_message(role='user', message=ru_message)
    message_obj.create_message(role='assistant', message=response)

    messages.pop()
    

    
