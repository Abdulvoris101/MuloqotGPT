from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound, DetailedAiogramError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot, logger
from db.state import FeedbackMessageState
from apps.common.filters.bound_filters import isBotMentioned
from apps.admin.events import sendError
from apps.common.exception import AiogramException, InvalidRequestException, ForbiddenException
from .keyboards import feedbackMarkup, cancelMarkup
from .managers import ChatActivityManager, MessageManager
from utils.translate import translateMessage
from utils import settings, containsAnyWord
from apps.subscription.managers import SubscriptionManager, PlanManager
import utils.text as text
import asyncio

from .models import ChatActivity
from .schemes import ChatActivityViewScheme
from .utility_handlers import TextMessageHandler, ImageMessageHandler
from ..subscription.models import ChatQuota, Limit
from ..subscription.schemes import ChatQuotaGetScheme

coreRouter = Router(name="coreRouter")


@coreRouter.message((~F.text.startswith(('/', "Bekor qilish")) & F.chat.type == "private"))
@coreRouter.message(isBotMentioned())
async def handleMessages(message: types.Message, chat: types.Chat):
    progressMessage = await bot.send_message(chat_id=chat.id,
                                             text="⏳")

    try:
        if containsAnyWord(message.text, settings.IMAGE_GENERATION_WORDS):
            return await ImageMessageHandler(message=message).handle()
        return await TextMessageHandler(message=message).handle()

    except ForbiddenException as e:
        logger.warn(e.message_text)
        return await message.reply(e.message_text)

    except AiogramException as e:
        logger.error(e.message_text)
        return await message.reply(e.message_text)

    except InvalidRequestException as e:
        logger.error(e.messageText)
        await sendError(text.GPT_ERROR_TEMPLATE.format(message=e.messageText,chatId=chat.id,
                                                       apiToken=e.apiKey))
        return await message.reply(text.CHATGPT_SERVER_ERROR)
    except TelegramBadRequest as e:
        logger.error(e.message)
        return await message.reply(text.SERVER_ERROR_TRY_AGAIN)
    finally:
        await bot.delete_message(chat_id=chat.id, message_id=progressMessage.message_id)


@coreRouter.message(Command("start"))
async def sendWelcome(message: types.Message, chat: types.Chat):
    streamingText = text.GREETINGS_TEXT
    messageChunkSize = 20
    updateInterval = 0.1

    try:
        msg = await bot.send_message(chat.id, streamingText[:messageChunkSize])
        for i in range(20, len(streamingText), 20):
            await asyncio.sleep(updateInterval)
            await bot.edit_message_text(chat_id=chat.id, message_id=msg.message_id,
                                        text=streamingText[:i + 10])
    except DetailedAiogramError as e:
        logger.exception("An error occured", exc_info=e.message)
        return message.reply(text.SERVER_ERROR_TRY_AGAIN)


@coreRouter.message(Command("profile"))
async def profile(message: types.Message, chat: types.Chat):
    subscription = SubscriptionManager.getChatCurrentSubscription(chatId=chat.id)
    userPlan = PlanManager.get(subscription.planId)
    userLimits = Limit.get(userPlan.limitId)

    try:
        activity = ChatActivity.getOrCreate(chat.id).to_dict()
        activity["currentMonthMessages"] = MessageManager.getUserMessagesTimeFrame(chatId=chat.id, days=31,
                                                                                   messageType='message')
        activity["currentMonthImages"] = MessageManager.getUserMessagesTimeFrame(chatId=chat.id, days=31,
                                                                                 messageType='image')
        activity["availableGptRequests"] = userLimits.monthlyLimitedGptRequests
        activity["availableImageRequests"] = userLimits.monthlyLimitedImageRequests
        chatActivityScheme = ChatActivityViewScheme(**activity)
        chatQuotaScheme = ChatQuotaGetScheme(**ChatQuota.getOrCreate(chat.id).to_dict())

        profileText = text.getProfileText(plantTitle=userPlan.title, chatActivityScheme=chatActivityScheme,
                                          chatQuotaScheme=chatQuotaScheme)

        return await message.answer(profileText)

    except TelegramBadRequest as e:
        logger.exception("An error occured", exc_info=e.message)
        return message.reply(text.SERVER_ERROR_TRY_AGAIN)


@coreRouter.message(Command("feedback"))
async def feedback(message: types.Message, chat: types.Chat):
    await bot.send_message(chat.id, text.REQUEST_FEEDBACK_MESSAGE, reply_markup=feedbackMarkup)


@coreRouter.message(Command("help"))
async def helpCommand(message: types.Message):
    await message.answer(text.HELP_COMMAND)


@coreRouter.callback_query(F.data == "feedback_callback")
async def feedbackCallback(callback: types.CallbackQuery, user: types.User, state: FSMContext):
    """ Feedback callback"""
    await callback.answer("")
    await bot.delete_message(user.id, callback.message.message_id)
    await bot.send_message(chat_id=user.id, text=text.FEEDBACK_GUIDE_MESSAGE,
                           reply_markup=cancelMarkup)

    await state.set_state(FeedbackMessageState.text)


@coreRouter.callback_query(F.data == "translate_callback")
async def translateCallback(callback: types.CallbackQuery, user: types.User):
    await callback.answer("")

    payedSubscription = SubscriptionManager.getActiveSubscription(user.id,
                                                                  PlanManager.getPremiumPlanId())

    chatActivity = ChatActivity.getOrCreate(chatId=user.id)

    if chatActivity.translatedMessagesCount >= 5 and payedSubscription is None:
        return await bot.send_message(chat_id=user.id, text=text.LIMIT_TRANSLATION_REACHED)

    ChatActivityManager.incrementActivityCount(user.id, "translatedMessagesCount")
    translatedMessage = translateMessage(callback.message.text, "auto",
                                         "uz", isTranslate=True)

    await bot.edit_message_text(
        chat_id=user.id,
        message_id=callback.message.message_id,
        text=translatedMessage)


@coreRouter.message(FeedbackMessageState.text)
async def setFeedbackMessage(message: types.Message, user: types.User, state: FSMContext):
    data = {**user.model_dump(), "text": text}
    await bot.send_message(settings.COMMENTS_GROUP_ID,
                           text.FEEDBACK_MESSAGE_EVENT_TEMPLATE.format_map(data))
    await state.clear()
    return await message.answer(text.THANK_YOU_TEXT)


# Callbacks for feeedback cancelation
@coreRouter.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, user: types.User, state: FSMContext):
    try:
        await bot.delete_message(user.id, callback.message.message_id)
    except TelegramNotFound as e:
        logger.exception("An error occured", exc_info=e.message)

    await callback.answer(text.CANCELED_TEXT)
    await state.clear()


@coreRouter.message(F.text == "Bekor qilish")
async def cancelButton(message: types.Message, state: FSMContext):
    await state.clear()
    return await bot.send_message(message.chat.id, text.CANCELED_TEXT, reply_markup=types.ReplyKeyboardRemove())


# events


@coreRouter.chat_member(F.NEW_CHAT_MEMBERS)
async def newChatMember(message: types.Message):
    new_chat_members = message.new_chat_members

    for member in new_chat_members:
        await bot.send_message(message.chat.id, text.NEW_CHAT_MEMBER_TEMPLATE.format(firstName=member.first_name))
