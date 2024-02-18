from bot import dp, bot, types
from apps.gpt import requestGpt
from filters.core import isBotMentioned, isGroupAllowed
from .managers import ChatManager, MessageManager, ChatActivityManager
from utils.translate import translateMessage, detect
from utils import checkTokens, countTokenOfMessage, constants, containsAnyWord
from apps.subscription.managers import SubscriptionManager, PlanManager, LimitManager
from aiogram.utils.exceptions import BadRequest
from apps.imageai.handlers import handleArt
import utils.text as text
import asyncio


class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chatId = message.chat.id
        self.full_name = message.chat.full_name
        self.text = str(message.text)

    async def __call__(self, *args, **kwargs):
        await ChatManager.activate(self.message)

    async def sendMessage(self, message, *args, **kwargs):
        if self.message.chat.type == "private":
            return await self.message.answer(message, *args, **kwargs)
        else:
            try:
                return await self.message.reply(message, *args, **kwargs)
            except BadRequest:
                return await self.message.answer(message, *args, **kwargs)

    async def isPermitted(self):
        if not LimitManager.checkGptRRequestsDailyLimit(self.chatId):
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

        message_en = translateMessage(self.text, self.chatId,
                                      lang='en', is_translate=self.isTranslate)

        return self.text if message_en is None else message_en

    async def handle(self):
        if not await self.isPermitted():
            return

        progressMessage = await self.sendMessage(text.PROCESSING_MESSAGE)

        # Save to message of user messages an assistant role
        MessageManager.userRole(await self.getTranslatedMessage(), self.message)

        messages = await self.trimMessageTokens()

        await self.message.answer_chat_action("typing")

        await asyncio.create_task(
            self.sendToGpt(messages, self.chatId, progressMessage.message_id))

    async def sendToGpt(self, messages, chatId, progressMessageId):
        try:
            response = await requestGpt(messages,  chatId,
                                        SubscriptionManager.isPremiumToken(chatId=chatId))

            translatedResponse = MessageManager.assistantRole(message=response, instance=self.message,
                                                              is_translate=self.isTranslate)

            await bot.delete_message(chatId, progressMessageId)

            try:
                # Send the AI response to the user
                await self.sendMessage(str(translatedResponse), disable_web_page_preview=True,
                                       parse_mode=types.ParseMode.MARKDOWN)
            except Exception as e:
                await self.sendMessage(text.ENTER_AGAIN, disable_web_page_preview=True,
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
async def handle_private_messages(message: types.Message):
    if not isGroupAllowed(message.chat.type, message.chat.id):
        return await message.answer(
            text.NOT_AVAILABLE_GROUP)

    if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS):
        return await handleArt(message)

    await AIChatHandler(message=message).handle()


@dp.message_handler(isBotMentioned())
async def handle_group_reply(message: types.Message):
    if not isGroupAllowed(message.chat.type, message.chat.id):
        return await message.answer(
            text.NOT_AVAILABLE_GROUP)

    return await AIChatHandler(message=message).handle()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    status = await ChatManager.activate(message)
    userChat = message.chat

    # if it is group, check is group available !
    if not status:
        return await message.answer(text.NOT_AVAILABLE_GROUP)

    await message.answer(text.getGreetingsText(message.from_user.first_name))

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
    userChat = message.chat

    premium = SubscriptionManager.findByChatIdAndPlanId(
        chatId=userChat,
        planId=PlanManager.getPremiumPlanId())

    await message.answer(text.getProfileText(
        "Premium" if premium is not None else "Free",
        ChatActivityManager.getTodayMessages(userChat.id),
        ChatActivityManager.getTodayImages(userChat.id)
    ))


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text.HELP_COMMAND)


@dp.message_handler(commands=['info'])
async def ability(message: types.Message):
    await message.answer(text.ABILITY_COMMAND)
