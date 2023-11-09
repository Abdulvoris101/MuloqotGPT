from bot import dp, bot, types
from apps.gpt import request_gpt
from .models import Chat
from .managers import ChatManager, MessageManager
from .keyboards import joinChannelMenu, settingsMenu
from filters.core import UserFilter
from filters import IsReplyFilter
from utils.translate import translate_message
from utils import count_tokens
import utils.text as text
import asyncio

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
        if count_tokens(messages) >= 2000:
            return True

        return False

    async def trim_message_tokens(self):
        messages = MessageManager.all(self.chat_id)

        if await self.check_tokens(messages):
            MessageManager.delete_by_limit(self.chat_id)
            return await self.trim_message_tokens()
        
        return messages

    async def get_en_message(self):
        message_en = translate_message(self.text, self.chat_id, lang='en')
        message_en = self.text if message_en is None else message_en

        return message_en

    async def handle(self):

        await UserFilter.activate(self.message, self.chat_id)

        proccess_message = await self.reply_or_send(self.PROCESSING_MESSAGE)
        
        message_en = await self.get_en_message() # translate message to en

        MessageManager.user_role(translated_text=message_en, instance=self.message)

        messages = await self.trim_message_tokens()

        await self.message.answer_chat_action("typing")

        asyncio.create_task(self.process_gpt_request(messages, self.chat_id, proccess_message))


    
    async def process_gpt_request(self, messages, chat_id, proccess_message):
        try:
            response = await request_gpt(messages, chat_id)
            response_uz = MessageManager.assistant_role(translated_text=response, instance=self.message)

            await bot.delete_message(chat_id, proccess_message.message_id)

            try:
                # Send the AI response to the user
                await self.reply_or_send(str(response_uz), disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
            except Exception as e:
                await self.reply_or_send(self.ERROR_MESSAGE, disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
       
        except Exception as e:
            print("Exception proccess",  e)
            # Handle errors from request_gpt
            await self.reply_or_send("Iltimos 5s dan keyin qayta urinib ko'ring!")


# handly reply and private messages
@dp.message_handler(lambda message: not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅') and message.chat.type == 'private')
async def handle_private_messages(message: types.Message):
    chat = AIChatHandler(message=message)

    
    await chat.handle()


# @dp.message_handler(IsReplyFilter())
# async def handle_reply(message: types.Message):
#     chat = AIChatHandler(message=message)

#     await chat.handle()


# Basic commands 


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message): 

    await message.answer(text.START_COMMAND)


    await message.answer(text.HOW_TO_HELP_TEXT)
    await ChatManager.activate(message)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(text.HELP_COMMAND)

# @dp.message_handler(commands=["groupinfo"])
# async def groupinfo(message: types.Message):
#     await message.answer(text.GROUP_INFO_COMMAND)


@dp.message_handler(commands=['info'])
async def ability(message: types.Message):
    await message.answer(text.ABILITY_COMMAND)


@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    if not await UserFilter.is_active(message.chat.id):
        return await message.answer("Muloqotni boshlash uchun - /start")

    await message.answer("⚙️ Sozlamalar", reply_markup=settingsMenu(message.chat.id))

# # Handle calbacks 
# @dp.callback_query_handler(text="check_subscription")
# async def check_issubscripted(message: types.Message):
#     if await UserFilter.is_subscribed(message.message.chat.type, message.message.chat.id):
#         await ChatManager.activate(message)

#         return await bot.send_message(message.message.chat.id, text.GREETINGS_TEXT)

#     return await message.answer("Afsuski siz kanallarga obuna bo'lmagansiz 😔")


# Auto translate
@dp.callback_query_handler(text="toggle_translate")
async def toggle_translate(message: types.Message):
    
    chat = Chat.get(message.message.chat.id)
    condition = not chat.auto_translate
    chat.auto_translate = condition
    chat.save()

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
