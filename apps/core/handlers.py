from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BadRequest
from bot import dp, bot, types
from apps.gpt import GptRequest
from filters.bound_filters import isBotMentioned
from utils.exception import AiogramException
from .managers import ChatManager, MessageManager, ChatActivityManager
from utils.translate import translateMessage, detect
from utils import checkTokens, countTokenOfMessage, constants, containsAnyWord
from apps.subscription.managers import SubscriptionManager, PlanManager, LimitManager
from apps.imageai.handlers import handleArt
import utils.text as text
import asyncio

# todo: check each handler


class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chatId = int(message.chat.id)
        self.full_name = message.chat.full_name
        self.text = str(message.text)

    async def sendMessage(self, message, *args, **kwargs):
        if self.message.chat.type == "private":
            sentMessage = await bot.send_message(self.chatId, message, *args, **kwargs)
            return sentMessage.message_id
        else:
            try:
                sentMessage = await self.message.reply(message, *args, **kwargs)
                return sentMessage.message_id
            except BadRequest:
                sentMessage = await bot.send_message(self.chatId, message, *args, **kwargs)
                return sentMessage.message_id

    async def isPermitted(self):
        if not LimitManager.checkRequestsDailyLimit(self.chatId, messageType="GPT"):
            if self.message.chat.type in constants.AVAILABLE_GROUP_TYPES:
                await self.sendMessage(text.LIMIT_GROUP_REACHED)
                return False

            await self.sendMessage(text.getLimitReached(
                    SubscriptionManager.isPremiumToken(self.chatId)
                ))

            return False

        if countTokenOfMessage(self.text) >= 300:
            await self.sendMessage(text.TOKEN_REACHED)
            return False

        return True

    async def trimMessageTokens(self):
        messages = MessageManager.all(self.chatId)

        if checkTokens(messages):
            MessageManager.deleteByLimit(self.chatId)
            return await self.trimMessageTokens()

        return messages

    async def getTranslatedMessage(self):
        try:
            lang_code = detect(self.text)
        except:
            lang_code = "en"

        self.isTranslate = True if lang_code == "uz" else False

        message_en = translateMessage(message=self.text,
                                      to='en', isTranslate=self.isTranslate)

        return self.text if message_en is None else message_en

    async def handle(self):
        if not await self.isPermitted():
            return

        MessageManager.userRole(await self.getTranslatedMessage(), self.message)

        messages = await self.trimMessageTokens()

        await bot.send_chat_action(chat_id=self.chatId, action="typing")

        await asyncio.create_task(
            self.sendToGpt(messages=messages,
                           chatId=self.chatId,
                           progressMessageId=await self.sendMessage(text.PROCESSING_MESSAGE)))

    async def sendToGpt(self, messages, chatId, progressMessageId):
        try:
            gptRequest = GptRequest(chatId,
                                    SubscriptionManager.isPremiumToken(chatId=chatId))

            try:
                response = await gptRequest.requestGpt(messages)
            except AiogramException as e:
                await bot.delete_message(chatId, progressMessageId)
                await self.sendMessage(e.message_text, disable_web_page_preview=True,
                                       parse_mode=types.ParseMode.MARKDOWN)
                return

            translatedResponse = MessageManager.assistantRole(message=response, instance=self.message,
                                                              is_translate=self.isTranslate)
            await bot.delete_message(chatId, progressMessageId)
            await self.sendMessage(str(translatedResponse), disable_web_page_preview=True,
                                   parse_mode=types.ParseMode.MARKDOWN)

        except Exception as e:
            print("Exception proccess", e)
            # Handle errors from requestGpt
            await self.sendMessage(text.ENTER_AGAIN)


@dp.message_handler(lambda message: all([
    not message.text.startswith('/'),
    not message.text.endswith('.!'),
    not message.text.startswith('✅'),
    not message.text.startswith("Bekor qilish"),
    message.chat.type == 'private'
]))
async def handlePrivateMessages(message: types.Message):
    userChat = message.chat
    status = await ChatManager.activate(message)

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS):
        return await handleArt(message)

    await AIChatHandler(message=message).handle()


@dp.message_handler(isBotMentioned())
async def handleGroupReply(message: types.Message):
    userChat = message.chat
    requestType = "IMAGE" if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS) else "GPT"
    status = await ChatManager.activate(message, requestType=requestType)

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS):
        return await handleArt(message)

    await AIChatHandler(message=message).handle()


@dp.message_handler(commands=['start'])
async def sendWelcome(message: types.Message):
    status = await ChatManager.activate(message)
    userChat = message.chat

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    await bot.send_message(userChat.id, text.getGreetingsText(message.from_user.first_name))

    planId = PlanManager.getFreePlanId() if userChat.type == "private" \
        else PlanManager.getHostPlanId()
    isFree = True if userChat.type == "private" else False

    SubscriptionManager.getSubscriptionOrCreate(
        planId=planId,
        chatId=userChat.id,
        is_paid=True,
        isFree=isFree
    )


@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    userChat = message.from_user

    premium = SubscriptionManager.getPremiumSubscription(
        chatId=userChat.id,
        planId=PlanManager.getPremiumPlanId())
    try:
        return await message.answer(text.getProfileText(
            "Premium" if premium is not None else "Free",
            ChatActivityManager.getTodayMessages(userChat.id),
            ChatActivityManager.getTodayImages(userChat.id)
        ))
    except BadRequest:
        print("Bot blocked")


@dp.message_handler(commands=['help'])
async def helpCommand(message: types.Message):
    await message.answer(text.HELP_COMMAND)


@dp.message_handler(Text(equals="Bekor qilish"), state='*')
async def cancelSubscription(message: types.Message, state: FSMContext):
    await state.finish()
    return await bot.send_message(message.chat.id, "Obuna bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())
