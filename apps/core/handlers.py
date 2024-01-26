from bot import dp, bot, types
from apps.gpt import requestGpt
from .models import Chat
from .managers import ChatManager, MessageManager
from .keyboards import settingsMenu
from filters.core import UserFilter
from utils.translate import translate_message
from utils import countTokens, countTokenOfMessage
from aiogram.dispatcher import FSMContext
import utils.text as text
import asyncio
from apps.subscription.managers import SubscriptionManager, PlanManager, LimitManager


class AIChatHandler:
    PROCESSING_MESSAGE = "⏳..."
    ERROR_MESSAGE = "Iltimos boshqatan so'rov yuboring"
    TOKEN_REACHED = "Savolni qisqartiribroq yozing"

    def __init__(self, message):
        self.message = message
        self.chatId = message.chat.id
        self.full_name = message.chat.full_name
        self.text = str(message.text)

    async def reply_or_send(self, message, *args, **kwargs):
        if self.message.chat.type == "private":
            return await self.message.answer(message, *args,  **kwargs)
        else:
            return await self.message.reply(message, *args, **kwargs)
    
    async def check_tokens(self, messages):
        if countTokens(messages) >= 200:
            return True

        return False

    async def trim_message_tokens(self):
        messages = MessageManager.all(self.chatId)
                
        if await self.check_tokens(messages):
            MessageManager.deleteByLimit(self.chatId)
            return await self.trim_message_tokens()
        
        return messages

    async def get_en_message(self):
        message_en = translate_message(self.text, self.chatId, lang='en')
        message_en = self.text if message_en is None else message_en

        return message_en


    async def handle(self):

        await UserFilter.activate(self.message, self.chatId)
        
        if not LimitManager.checkGptRRequestsDailyLimit(self.chatId):
            await self.reply_or_send(text.LIMIT_REACHED)
            return 

        tokens_of_message = countTokenOfMessage(self.text)
        
        if tokens_of_message >= 200:
            return await self.reply_or_send(self.TOKEN_REACHED)

        
        proccess_message = await self.reply_or_send(self.PROCESSING_MESSAGE)
        
        message_en = await self.get_en_message() # translate message to en

        MessageManager.userRole(translated_text=message_en, instance=self.message)

        messages = await self.trim_message_tokens()

        await self.message.answer_chat_action("typing")
        
        asyncio.create_task(self.process_gpt_request(messages, self.chatId, proccess_message))


    async def process_gpt_request(self, messages, chatId, proccess_message):
        try:
            
            if SubscriptionManager.isPremiumToken(chatId=chatId):
                response = await requestGpt(messages, chatId, True)
            else:
                response = await requestGpt(messages, chatId, False)
                
            
            response_uz = MessageManager.assistantRole(message=response, instance=self.message)

            await bot.delete_message(chatId, proccess_message.message_id)

            try:
                # Send the AI response to the user
                await self.reply_or_send(str(response_uz), disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
            except Exception as e:
                await self.reply_or_send(self.ERROR_MESSAGE, disable_web_page_preview=True, parse_mode=types.ParseMode.MARKDOWN)
       
        except Exception as e:
            print("Exception proccess",  e)
            # Handle errors from requestGpt
            await self.reply_or_send("Iltimos 5 sekund dan keyin qayta urinib ko'ring!")


# handly reply and private messages
@dp.message_handler(lambda message: not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅') and message.chat.type == 'private')
async def handle_private_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        chat = AIChatHandler(message=message)
        await chat.handle()
        return
    
    state.finish()
    await message.answer("Xatolik ketdi, qayta boshlang")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message): 

    await message.answer(text.START_COMMAND)
    await message.answer(text.getGreetingsText(message.from_user.first_name))
    
    user_subscription = SubscriptionManager.getByChatId(chatId=message.from_user.id)
    
    if user_subscription is None:
        SubscriptionManager.createSubscription(
            planId=PlanManager.getFreePlanOrCreate().id,
            chatId=message.from_user.id,
            is_paid=True,
            isFree=True
        )
    
    await ChatManager.activate(message)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(text.HELP_COMMAND)


@dp.message_handler(commands=['info'])
async def ability(message: types.Message):
    await message.answer(text.ABILITY_COMMAND)


@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    if not await UserFilter.isActive(message.chat.id):
        return await message.answer("Muloqotni boshlash uchun - /start")

    await message.answer("⚙️ Sozlamalar", reply_markup=settingsMenu(message.chat.id))


# Auto translate
@dp.callback_query_handler(text="toggle_translate")
async def toggle_translate(message: types.Message):
    
    chat = Chat.get(message.message.chat.id)
    condition = not chat.autoTranslate
    chat.autoTranslate = condition
    chat.save()

    text = "Tarjimon Yoqildi" if condition else "Tarjimon O'chirildi"

    await bot.edit_message_text(chat_id=message.message.chat.id,
                            message_id=message.message.message_id,
                            text="⚙️ Sozlamalar", reply_markup=settingsMenu(chatId=message.message.chat.id))

    await message.answer(text)
    

# Close inline
@dp.callback_query_handler(text="close")
async def close(message: types.Message):
    await bot.delete_message(chat_id=message.message.chat.id, message_id=message.message.message_id)
