import time
from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound
from aiogram.filters import Command, CommandObject, or_f, and_f, CommandStart
from aiogram.fsm.context import FSMContext
from bot import bot
from apps.gpt import GptRequest
from db.state import Comment
from filters.bound_filters import isBotMentioned
from utils.events import sendError, sendCommentEvent
from utils.exception import AiogramException
from utils.message import fixMessageMarkdown
from .keyboards import feedbackMarkup, cancelMarkup, messageMarkup
from .managers import ChatManager, MessageManager, ChatActivityManager
from utils.translate import translateMessage, detect
from utils import checkTokens, countTokenOfMessage, constants, containsAnyWord
from apps.subscription.managers import SubscriptionManager, PlanManager, LimitManager, ConfigurationManager
from apps.imageai.handlers import handleArt
import utils.text as text
import asyncio
from .models import ChatActivity
from ..subscription.models import ChatQuota

coreRouter = Router(name="coreRouter")


class AIChatHandler:
    def __init__(self, message):
        self.message = message
        self.chatId = int(message.chat.id)
        self.full_name = message.chat.full_name
        self.text = str(message.text)

    async def sendMessage(self, text, *args, **kwargs):
        if self.message.chat.type == "private":
            sentMessage = await bot.send_message(self.chatId, text, *args, **kwargs)
            return sentMessage.message_id
        else:
            try:
                sentMessage = await self.message.reply(text, *args, **kwargs)
                return sentMessage.message_id
            except TelegramBadRequest:
                sentMessage = await bot.send_message(self.chatId, text, *args, **kwargs)
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

    async def getFeedback(self):
        chatActivity = ChatActivity.get(self.chatId)
        configuration = ConfigurationManager.getFirst()

        if configuration.isBeta:
            if chatActivity.allMessages == 10 and self.message.chat.type == "private":
                await bot.send_message(self.chatId, text.FEEDBACK_MESSAGE, reply_markup=feedbackMarkup)

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
            validatedText = fixMessageMarkdown(translatedResponse)

            markup = messageMarkup if self.message.chat.type == "private" and not self.isTranslate else None

            await self.sendMessage(str(validatedText), disable_web_page_preview=True,
                                   parse_mode=types.ParseMode.MARKDOWN, reply_markup=markup)

            time.sleep(2)
            await self.getFeedback()

        except Exception as e:
            await sendError(str(e))
            await self.sendMessage(text.ENTER_AGAIN)


@coreRouter.message((~F.text.startswith(('/', '✅', "Bekor qilish")) &
                    ~F.text.endswith('.!') & F.chat.type == "private"))
async def handlePrivateMessages(message: types.Message):
    print("True")
    userChat = message.chat
    status = await ChatManager.activate(message)

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS):
        return await handleArt(message)

    await AIChatHandler(message=message).handle()


@coreRouter.message(isBotMentioned())
async def handleGroupReply(message: types.Message):
    userChat = message.chat
    requestType = "IMAGE" if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS) else "GPT"
    status = await ChatManager.activate(message, requestType=requestType)

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    if containsAnyWord(message.text, constants.IMAGE_GENERATION_WORDS):
        return await handleArt(message)

    await AIChatHandler(message=message).handle()


@coreRouter.message(Command("start"))
async def sendWelcome(message: types.Message):
    status = await ChatManager.activate(message)
    userChat = message.chat

    if not status:
        return await bot.send_message(userChat.id, text.NOT_AVAILABLE_GROUP)

    streaming_text = text.getGreetingsText(message.from_user.first_name)

    msg = await bot.send_message(userChat.id, streaming_text[:20])

    # Stream the remaining text
    for i in range(20, len(streaming_text), 20):
        await asyncio.sleep(0.1)  # Adjust the delay between messages as needed
        try:
            await bot.edit_message_text(chat_id=userChat.id, message_id=msg.message_id, text=streaming_text[:i + 10])
        except Exception as e:
            pass

    planId = PlanManager.getFreePlanId() if userChat.type == "private" \
        else PlanManager.getHostPlanId()
    isFree = True if userChat.type == "private" else False

    SubscriptionManager.getSubscriptionOrCreate(
        planId=planId,
        chatId=userChat.id,
        is_paid=True,
        isFree=isFree
    )


@coreRouter.message(Command("profile"))
async def profile(message: types.Message):
    userChat = message.from_user

    premium = SubscriptionManager.getPremiumSubscription(
        chatId=userChat.id,
        planId=PlanManager.getPremiumPlanId())
    try:

        return await message.answer(text.getProfileText(
            "Premium" if premium is not None else "Free",
            ChatActivityManager.getTodayMessagesCount(userChat.id),
            ChatActivityManager.getTodayImages(userChat.id),
            ChatQuota.getOrCreate(userChat.id).additionalGptRequests,
            ChatQuota.getOrCreate(userChat.id).additionalImageRequests,
        ))
    except TelegramBadRequest:
        print("Bot blocked")


@coreRouter.message(Command("feedback"))
async def feedback(message: types.Message):
    userChat = message.from_user
    await bot.send_message(userChat.id, text.FEEDBACK_MESSAGE, reply_markup=feedbackMarkup)


@coreRouter.message(Command("help"))
async def helpCommand(message: types.Message):
    await message.answer(text.HELP_COMMAND)


# Callbacks for feeedback
@coreRouter.callback_query(F.data == "feedback_callback")
async def feedbackCallback(callback: types.CallbackQuery, state: FSMContext):
    user = callback.from_user

    await callback.answer("Izoh qoldirish")
    await bot.delete_message(user.id, callback.message.message_id)

    await bot.send_message(
        chat_id=user.id,
        text=text.FEEDBACK_GUIDE_MESSAGE,
        reply_markup=cancelMarkup)

    await state.set_state(Comment.message)


@coreRouter.callback_query(F.data == "translate_callback")
async def translateCallback(callback: types.CallbackQuery):
    user = callback.from_user

    payedSubscription = SubscriptionManager.getPremiumSubscription(
        user.id, PlanManager.getPremiumPlanId())

    if ChatActivityManager.getTranslatedMessageCounts(user.id) >= 5 and payedSubscription is None:
        return await bot.send_message(
            chat_id=user.id,
            text=text.LIMIT_TRANSLATION_REACHED)

    ChatActivityManager.increaseActivityField(user.id, "translatedMessagesCount")
    translatedMessage = translateMessage(callback.message.text, "auto",
                                         "uz", isTranslate=True)

    await bot.edit_message_text(
        chat_id=user.id,
        message_id=callback.message.message_id,
        text=translatedMessage)


@coreRouter.message(Comment.message)
async def setFeedbackMessage(message: types.Message, state: FSMContext):
    feedbackMessage = f"""#chat-id: {message.from_user.id}
#username: @{message.from_user.username}
#xabar: \n\n{message.text}
    """

    await sendCommentEvent(feedbackMessage)
    await state.clear()
    return await message.answer("Izoh uchun rahmat!")


# Callbacks for feeedback cancelation
@coreRouter.callback_query(F.data == "cancel")
async def cancelInlineFeedback(callback: types.CallbackQuery, state: FSMContext):
    user = callback.from_user

    try:
        await bot.delete_message(user.id, callback.message.message_id)
    except TelegramNotFound:
        pass

    await callback.answer("Bekor qilindi!")
    await state.clear()


@coreRouter.message(F.text == "Bekor qilish")
async def cancelButton(message: types.Message, state: FSMContext):
    await state.clear()
    return await bot.send_message(message.chat.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


# events


@coreRouter.message(F.NEW_CHAT_MEMBERS)
async def newChatMember(message: types.Message):
    new_chat_members = message.new_chat_members

    for member in new_chat_members:
        await bot.send_message(message.chat.id, text.getNewChatMember(member.first_name))
