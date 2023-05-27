from app import dp, bot, types
from .utils import translate_message, IsReplyFilter
from main import answer_ai
from db.models import Message, Chat, session


class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chat_id = message.chat.id
        self.full_name = message.chat.full_name
        self.text = message.text

    async def is_active(self):
        chat = session.query(Chat.is_activated).filter_by(chat_id=self.chat_id).first()

        if chat is None:
            return False

        return chat.is_activated
    
    def is_group(self, messages):
        return len(messages) <= 2 and self.message.chat.type != 'private'

    async def process_ai_message(self):
        message_ru = translate_message(self.text, lang='ru')
        messages = Message.all(self.chat_id)

        if not await self.is_active():
            return await self.message.answer("Muloqotni boshlash uchun - /startai")

        content = message_ru + '😂' if self.is_group(messages) else message_ru

        msg = Message.user_role(content=content, instance=self.message)
        messages.append(msg)

        response = answer_ai(messages, chat_id=self.chat_id)
        response_uz = Message.assistant_role(content=response, instance=self.message)

        await self.message.reply(response_uz)


@dp.message_handler(lambda message: not message.text.startswith('/') and not message.text.startswith('.') and message.chat.type == 'private')
async def handle_private_messages(message: types.Message):
    chat = AIChatHandler(message=message)

    return await chat.process_ai_message()


@dp.message_handler(IsReplyFilter())
async def handle_reply(message: types.Message):
    chat = AIChatHandler(message=message)
    return await chat.process_ai_message()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("""🤖 Salom! Men MuloqotAi, sizning shaxsiy AI yordamchingizman, sizga qiziqarli va ulashingizga imkon beradigan suhbat tajribasi taqdim etish uchun yaratilganman 😉. Ochiq guruh - @muloqataigr""")
    await message.answer("""Endi muloqotai guruhda xam ishlaydi - /groupinfo.\nMeni boshqa chatbotlardan farq qilishim - /me!\nBatafsil ma'lumot uchun - /help""")


@dp.message_handler(commands=['groupinfo'])
async def send_group_info(message: types.Message):
    await message.answer("""Men endi guruhlar bilan ham ishlash imkoniyatiga egaman. Bu sizning guruhingizdagi a'zolar bilan birga muloqot qilishim va ularning savollari va talablari bo'yicha yordam berish imkonini beradi. Men bilan suxbat olib borish uchun shunchaki mening xabarimga reply qiling.\nShuningdek, Men guruh bilan hazil va latifalar bilan gaplashish imkoniyatiga egaman.""")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("""Shaxsiy va guruh suhbatlaringizda yordam beradigan foydali yordamchi! Ushbu botning guruhda ishlash tartibi quyidagicha:\n\n1️⃣ <b>Guruhga qo'shish</b>: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@muloqataibot" ni qidiring va uningni gruhga taklif qiling.\n\n2️⃣ <b>Admin huquqlarini berish</b>: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.\n\n3️⃣ <b>Gruhda suhbatlashish</b>: MuloqotAI gruhda /startai kommandasini kiritsangiz bot faol bo'ladi va u bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Guruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin. Agarda vaqtinchalik to'xtatib turmoqchi bo'lsangiz /stopai kommandasini yuboring.\n\n➕ <b>Qo'shimcha</b>: Xabarlarni botning lichkasida xam yubora olasiz\n""")


@dp.message_handler(commands=['me'])
async def me(message: types.Message):
    await message.answer("""💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, sizga aniqligi va maqbul javoblarni taklif etishim mumkin.\n\n🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.\n\n😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim!""")


@dp.message_handler(commands=['startai'])
async def activate(message: types.Message):
    chat = Chat(message.chat.id, message.chat.full_name)
    chat.activate(str(message.chat.type))
    await message.reply("MuloqotAi hozir faol holatda va sizga yordam berishga tayyor!")


@dp.message_handler(commands=['stopai'])
async def deactivate(message: types.Message):

    chat = session.query(Chat).filter_by(chat_id=message.chat.id).first()

    if chat is not None:
        chat.is_activated = False
        session.commit()

    await message.reply("MuloqotAi toxtatilindi. Muloqotni boshlash uchun - /startai")
