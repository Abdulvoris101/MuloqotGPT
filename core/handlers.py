from bot import dp, bot, types
from .utils import translate_message, IsReplyFilter, send_event
from gpt import answer_ai
from .models import Message, session, Chat
from .keyboards import joinChannelMenu, settingsMenu
import os
from db.proccessors import MessageProcessor
from aiogram.types import ChatActions

class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chat_id = message.chat.id
        self.full_name = message.chat.full_name
        self.text = str(message.text)

    @classmethod
    async def is_active(cls, chat_id):
        chat = session.query(Chat.is_activated).filter_by(chat_id=chat_id).first()

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


    async def reply_or_send(self, message, *args, **kwargs):
        if self.message.chat.type == "private":
            return await self.message.answer(message, *args,  **kwargs)
        else:
            return await self.message.reply(message, *args, **kwargs)

    async def process_ai_message(self):

        if not await self.is_active(self.chat_id):
            await activate(self.message)

        elif not await self.is_subscribed(self.message.chat.type, self.chat_id):
            return await self.message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)

        sent_message = await self.reply_or_send("⏳...")

        message_en = translate_message(self.text, self.chat_id, lang='en')

        messages = Message.all(self.chat_id)
        
        content = self.text if message_en is None else message_en

        msg = Message.user_role(content=content, instance=self.message)
        
        messages.append(msg)

        await self.message.answer_chat_action("typing")
        
        response = await answer_ai(messages, chat_id=self.chat_id)

        response_uz = Message.assistant_role(content=response, instance=self.message)

        await bot.delete_message(self.chat_id, sent_message.message_id)

        try:
            await self.reply_or_send(str(response_uz), disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
        except Exception as e:
            await self.reply_or_send("Iltimos boshqatan so'rov yuboring", disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)


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
    await message.answer("""🤖 Salom! Men MuloqotAi, sizning shaxsiy yordamchingizman.\nAvtotarjimon yoniq xolatda.\nBatafsil ma'lumot uchun - /help""")
    await message.answer("""Sizga qanday yordam bera olaman?""")

    if not await AIChatHandler.is_subscribed(message.chat.type, message.chat.id):
        return await message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)
    
    await activate(message)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("""<b>Bot qanday ishlaydi?</b>
Bot chatgpt va lexica ai ni rasm generatsiyasi uchun  ishlatadi. Siz chatgptni mutloq bepul  ishlatishingiz mumkin, lekin rasm generatsiya  qilish uchun aqsha sotib olishingiz kerak. Bitta rasm generatsiyasi  20 aqsha turadi, va xar bir foydalanuvchiga boshida 100 aqsha beriladi. Batafsil -> link

Bot qo'shimcha xususiyatlari:

🔹<b>Avtotarjima:</b> - bilasiz chatgpt o'zbek tilini tushunmaydi shuning uchun botda avtotarjima xususiyati mavjud, agarda avtotarjimani yoqib qo'ysangiz sizning xar bir so'rovingiz tarjimon orqali ingliz tilga  o'tqizilib chatgptga yuboriladi va  kelgan javob esa o'zbekchaga tarjima qilinadi. Bu bilan siz ingliz tilini bilmasdan turib chatgptni to'liqona ishlatishingiz mumkin bo'ladi. Avtotarjima mutlaqo bepul

🔹<b>Xazilkash AI:</b> muloqotai guruhlarda xam gaplasha oladi, qiziq tomoni u guruhlarda gaplashgan payti juda xam xazilkash tutadi. Siz bot bilan xuddi do'st kabi muloqot qila olasiz. Agarda siz  aniqroq javob olmoqchi bo'lsangiz uning o'ziga yozing

Botni guruhga qanday qo'shish bo'yicha batafsil ma'lumot - /groupinfo""")

@dp.message_handler(commands=["groupinfo"])
async def groupinfo(message: types.Message):
    await message.answer("""Shaxsiy va guruh suhbatlaringizda yordam beradigan foydali yordamchi! Ushbu botning <b>guruhda</b> ishlash tartibi quyidagicha:\n\n1️⃣ <b>Guruhga qo'shish</b>: MuloqotAIdan foydalanish uchun, uningni Telegram gruhingizga qo'shing. Bu uchun "@muloqataibot" ni qidiring va uningni gruhga taklif qiling.\n\n2️⃣ <b>Admin huquqlarini berish</b>: MuloqotAItning samarali ishlashi uchun uningni admin sifatida qo'shish kerak. Uningga to'g'ri admin huquqlarini berishni unutmang, masalan, xabarlarni o'chirish (ixtiyoriy) va boshqa sozlamalarni boshqarish.\n\n3️⃣ <b>Gruhda suhbatlashish</b>: Bot bilan suhbat qurish uchun unga reply tarzida so'rov yuboring. Guruh a'zolari savollarni so'rash, ma'lumot so'ralish, yordam so'ralish yoki qiziqarli suhbatlar olib borishlari mumkin.\n\n➕ <b>Qo'shimcha:</b> Men guruh bilan hazil va latifalar bilan gaplashish imkoniyatiga egaman.""")

@dp.message_handler(commands=['ability'])
async def ability(message: types.Message):
    await message.answer("""💡 Aqlli: Ko'plab mavzularni tushunish va javob berishga tayyorman. Umumiy bilimdan ma'lumotlarni qidirishga qadar, sizga aniqligi va maqbul javoblarni taklif etishim mumkin.\n\n🧠 Dono: Men doimiy o'rganish va rivojlanishda, yangi ma'lumotlarga va foydalanuvchi bilan bo'lishuvlarga moslashishim mumkin. Aqlli muloqotlarni taklif etishim mumkin.\n\n😄 Xushchaqchaq: Hayot kulguli tabassum bilan yaxshilanadi, va men sizning yuzingizga tabassum olib kelish uchun bu yerga keldim!\n\n🌄 Rassom: Mening yana bir qobilyatlarimdan biri bu rasm generatsiya qila olishim. Men sizga xar qanday turdagi ajoyib rasmlarni generatsiya qilib olib bera olaman\n\n⚙️ Avtotarjima: Meni siz bilan o'zbek tilida yanada yahshiroq muloqot qila olishim uchun, avtotarjima funksiyasini ishlataman. Endi siz ingliz tilida qiynalib menga yozishingiz shart emas. Bu funksiya ixtiyoriy xoxlagan paytiz o'chirib qo'yishingiz mumkin. """)


@dp.message_handler(commands=['startai'])
async def activate(message: types.Message):
    chat = Chat(message.chat.id, message.chat.full_name, message.chat.username)

    await chat.activate(str(message.chat.type))


@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    if not await AIChatHandler.is_active(message.chat.id):
        return await message.answer("Muloqotni boshlash uchun - /start")

    await message.answer("⚙️ Sozlamalar", reply_markup=settingsMenu(message.chat.id))


@dp.callback_query_handler(text="check_subscription")
async def check_issubscripted(message: types.Message):
    if await AIChatHandler.is_subscribed(message.message.chat.type, message.message.chat.id):
        await activate(message)
        return await bot.send_message(message.message.chat.id, "Assalomu aleykum Men Muloqot AI man sizga qanday yordam bera olaman?")

    return await message.answer("Afsuski siz kanallarga obuna bo'lmagansiz 😔")

# Auto translate
@dp.callback_query_handler(text="toggle_translate")
async def toggle_translate(message: types.Message):
    condition = Chat.toggle_set_translate(message.message.chat.id)
    text = "Tarjimon Yoqildi" if condition else "Tarjimon O'chirildi"

    await bot.edit_message_text(chat_id=message.message.chat.id,
                            message_id=message.message.message_id,
                            text="⚙️ Sozlamalar", reply_markup=settingsMenu(chat_id=message.message.chat.id))

    await message.answer(text)
    
# Close inline
@dp.callback_query_handler(text="close")
async def close(message: types.Message):
    await bot.delete_message(chat_id=message.message.chat.id, message_id=message.message.message_id)
    

# New chat event
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
