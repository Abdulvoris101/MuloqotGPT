from bot import dp, bot, types
from apps.gpt import request_gpt
from .models import Message, Chat
from .manager import ChatManager
from .keyboards import joinChannelMenu, settingsMenu
from filters.core import IsReplyFilter, UserFilter
from utils.translate import translate_message
from utils import count_tokens

import utils.text as text


class AIChatHandler:
    PROCESSING_MESSAGE = "⏳..."
    ERROR_MESSAGE = "Iltimos boshqatan so'rov yuboring"

    def __init__(self, message):
        self.message = message
        self.chat_id = message.chat.id
        self.full_name = message.chat.full_name
        self.text = str(message.text)
        

    async def reply_or_send(self, message, *args, **kwargs):
        if self.message.chat.type == "private":
            return await self.message.answer(message, *args,  **kwargs)
        else:
            return await self.message.reply(message, *args, **kwargs)
    
    async def check_tokens(self, messages):
        if count_tokens(messages) >= 3500:
            return True

        return False

    async def clear_message(self):
        messages = Message.all(self.chat_id)

        if await self.check_tokens(messages):
            Message.delete_by_limit(self.chat_id)
            await self.clear_message()
        else:
            return


    async def handle(self):

        # Ensure user activation and check entry to the channel
        await UserFilter.activate_and_check(self.message, self.chat_id)

        # Send a temporary message indicating processing
        sent_message = await self.reply_or_send(self.PROCESSING_MESSAGE)

        # Translate the message to English
        message_en = translate_message(self.text, self.chat_id, lang='en')

        # Get all messages for the chat

        await self.clear_message()

        messages = Message.all(self.chat_id)

        # Determine the content to use for AI processing
        content = self.text if message_en is None else message_en

        # Create a new user role message
        msg = Message.user_role(text=content, instance=self.message)
        
        # Append the user role message to the list of messages
        messages.append(msg)

        # Indicate typing to the user
        await self.message.answer_chat_action("typing")
        
        # Perform AI processing on the messages
        response = await request_gpt(messages, chat_id=self.chat_id)

        # Create an assistant role message for the AI response
        response_uz = Message.assistant_role(content=response, instance=self.message)

        # Delete the temporary processing message
        await bot.delete_message(self.chat_id, sent_message.message_id)
        
        try:
            # Send the AI response to the user
            await self.reply_or_send(str(response_uz), disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
        except Exception as e:
            await self.reply_or_send(self.ERROR_MESSAGE, disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(lambda message: not message.text.startswith('/') and not message.text.endswith('.!') and message.chat.type == 'private')
async def handle_private_messages(message: types.Message):
    chat = AIChatHandler(message=message)

    return await chat.handle()


@dp.message_handler(IsReplyFilter())
async def handle_reply(message: types.Message):
    chat = AIChatHandler(message=message)

    return await chat.handle()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message): 

    await message.answer(text.START_COMMAND)
    await message.answer(text.HOW_TO_HELP_TEXT)

    if not await UserFilter.is_subscribed(message.chat.type, message.chat.id):
        return await message.answer("Botdan foydalanish uchun quyidagi kannalarga obuna bo'ling", reply_markup=joinChannelMenu)
    
    await ChatManager.activate(message)

# Bot chatgpt va lexica ai ni rasm generatsiyasi uchun  ishlatadi. Siz chatgptni mutloq bepul  ishlatishingiz mumkin, lekin rasm generatsiya  qilish uchun aqsha sotib olishingiz kerak. Bitta rasm generatsiyasi  20 aqsha turadi, va xar bir foydalanuvchiga boshida 100 aqsha beriladi. Batafsil -> link


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(text.HELP_COMMAND)

@dp.message_handler(commands=["groupinfo"])
async def groupinfo(message: types.Message):
    await message.answer(text.GROUP_INFO_COMMAND)


@dp.message_handler(commands=['info'])
async def ability(message: types.Message):
    await message.answer(text.ABILITY_COMMAND)


@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    if not await UserFilter.is_active(message.chat.id):
        return await message.answer("Muloqotni boshlash uchun - /start")

    await message.answer("⚙️ Sozlamalar", reply_markup=settingsMenu(message.chat.id))

@dp.callback_query_handler(text="check_subscription")
async def check_issubscripted(message: types.Message):
    if await UserFilter.is_subscribed(message.message.chat.type, message.message.chat.id):
        await ChatManager.activate(message)
        return await bot.send_message(message.message.chat.id, text.GREETINGS_TEXT)

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
            await message.answer(text.NEW_MEMBER_TEXT)
