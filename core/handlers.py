from bot import dp, bot, types
from .utils import translate_message, IsReplyFilter, send_event
from gpt import answer_ai
from .models import Message, session, Chat
from .keyboards import joinChannelMenu
import os
from db.proccessors import MessageProcessor


class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chat_id = message.chat.id
        self.full_name = message.chat.full_name
        self.text = str(message.text)


    async def is_active(self):
        chat = session.query(Chat.is_activated).filter_by(chat_id=self.chat_id).first()

        if chat is None:
            return False

        return chat.is_activated
    

    @classmethod
    async def is_subscribed(cls, chat_type, user_id):
        if chat_type == 'private':
            channel_id = os.environ.get("CHANNEL_ID")

            chat_member = await bot.get_chat_member(channel_id, user_id)

            if chat_member.is_chat_member():
                return True

            return False

        return True
    

    def is_group(self, messages):
        if messages is None:
            MessageProcessor.create_system_messages(self.chat_id, self.message.chat.type)

        return len(messages) <= 2 and self.message.chat.type != 'private'

    async def process_ai_message(self):

        if not await self.is_active():
            return await self.message.answer("Muloqotni boshlash uchun - /startai")

        elif not await self.is_subscribed(self.message.chat.type, self.chat_id):
            return await self.message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)

        sent_message = await self.message.reply("⏳...")

        message_en = translate_message(self.text, lang='en')
        messages = Message.all(self.chat_id)
        
        content = f'{message_en} 😂' if self.is_group(messages) else message_en

        content = self.text if content is None else content

        msg = Message.user_role(content=content, instance=self.message)
        
        messages.append(msg)

        response = await answer_ai(messages, chat_id=self.chat_id)

        response_uz = Message.assistant_role(content=response, instance=self.message)

        try:
            await bot.edit_message_text(chat_id=self.chat_id, message_id=sent_message.message_id, text=str(response_uz), disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
        
        except Exception as e:
            await bot.edit_message_text(chat_id=self.chat_id, message_id=sent_message.message_id, text="Iltimos boshqatan so'rov yuboring", disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)



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
    await message.answer("""🤖 Salom! Men MuloqotAi, sizning shaxsiy AI yordamchingizman,\n\nKanal - @muloqotainews\nOchiq guruh - @muloqataigr.\nBatafsil ma'lumot uchun - /help""")

    if not await AIChatHandler.is_subscribed(message.chat.type, message.chat.id):
        return await message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)
    
    await activate(message)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("""Shaxsiy va guruh suhbatlaringizda yordam beradigan foydali yordamchi! Ushbu botning <b>guruhda</b> ishlash tartibi quyidagicha:\n\n1️⃣ <b>Guruhga qo'shish</b>: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@muloqataibot" ni qidiring va uningni gruhga taklif qiling.\n\n2️⃣ <b>Admin huquqlarini berish</b>: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.\n\n3️⃣ <b>Gruhda suhbatlashish</b>: Bot bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Guruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin.\n\n➕ <b>Qo'shimcha:</b> Men guruh bilan hazil va latifalar bilan gaplashish imkoniyatiga egaman.""")


@dp.message_handler(commands=['ability'])
async def ability(message: types.Message):
    await message.answer("""💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, sizga aniqligi va maqbul javoblarni taklif etishim mumkin.\n\n🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.\n\n😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim!\n\n🌄 Rassom: Mening yana bir qobilyatlarimdan biri bu rasm generatsiya qila olishim. Men sizga xar qanday turdagi ajoyib rasmlarni generatsiya qilib olib bera olaman\n\n⚙️ Avtotarjima: Meni siz bilan o'zbek tilida yanada yahshiroq muloqot qila olishim uchun, avtotarjima funksiyasini ishlataman. Endi siz ingliz tilida qiynalib menga yozishingiz shart emas. Bu funksiya ixtiyoriy xoxlagan paytiz o'chirib qo'yishingiz mumkin. """)


@dp.message_handler(commands=['startai'])
async def activate(message: types.Message):

    chat = Chat(message.chat.id, message.chat.full_name, message.chat.username)

    await chat.activate(str(message.chat.type))

    await message.reply("Assalomu aleykum Men Muloqot AI man sizga qanday yordam bera olaman ?")


@dp.callback_query_handler(text="check_subscription")
async def check_issubscripted(message: types.Message):
    if await AIChatHandler.is_subscribed(message.message.chat.type, message.message.chat.id):
        await activate(message)
        return await bot.send_message(message.message.chat.id, "Assalomu aleykum Men Muloqot AI man sizga qanday yordam bera olaman?")

    return await message.answer("Afsuski siz kanallarga obuna bo'lmagansiz 😔")



@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_chat_member_updated(message: types.Message):
    new_chat_members = message.new_chat_members
    bot_id = message.bot.id

    for member in new_chat_members:
        if member.id == bot_id:
            await message.answer(f"""👋 Assalomu alaykum! Mening ismim MuloqotAI 
Men sizga yordam berish uchun yaratilgan aqlli chatbotman. 
Bot ishlashi uchun menga administrator huquqlarini bering
😊 Ko'proq foydam tegishi uchun /help kommandasini yuborib men bilan yaqinroq tanishib chiqing
""")
