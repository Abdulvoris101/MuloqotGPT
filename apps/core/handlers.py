import json

from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound, DetailedAiogramError
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, CommandStart, CommandObject, \
    or_f, MEMBER, LEFT, JOIN_TRANSITION
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, ReplyKeyboardRemove
from aiogram.utils.chat_action import ChatActionSender

from bot import bot, logger
from db.state import FeedbackMessageState, ChooseGptModelState
from apps.common.filters.bound_filters import isBotMentioned, TextContentFilter
from apps.admin.events import sendError
from apps.common.exception import AiogramException, InvalidRequestException, ForbiddenException
from .keyboards import feedbackMarkup, cancelMarkup, profileMarkup, gptModelsMarkup
from .managers import ChatActivityManager, MessageManager, ChatManager
from utils.translate import translateMessage
from utils import settings, containsAnyWord
from apps.subscription.managers import SubscriptionManager, PlanManager, LimitManager, ChatQuotaManager
import utils.text as text
import asyncio

from .models import ChatActivity, Chat
from .schemes import ChatActivityViewScheme, ChatScheme
from .utility_handlers import TextMessageHandler, ImageMessageHandler
from ..subscription.models import ChatQuota, Limit
from ..subscription.schemes import ChatQuotaGetScheme

coreRouter = Router(name="coreRouter")


@coreRouter.message(CommandStart())
async def sendWelcome(message: types.Message, chat: types.Chat, command: CommandObject):
    referral = command.args
    ChatManager.assignReferredBy(chat.id, referral)

    if ChatManager.isValidReferral(chat.id, referral):
        referredUser = Chat.get(int(referral))
        chatScheme = ChatScheme(**referredUser.to_dict())
        chatScheme.referralUsers.append(chat.id)
        referredUser.referralUsers = chatScheme.model_dump().get("referralUsers")
        referredUser.save()

        ChatQuotaManager.incrementCount(int(referral), "additionalGpt3Requests", 10)

        await bot.send_message(referredUser.chatId, text.CONGRATS_GAVE_REQUESTS)

    return await TextMessageHandler(message).sendStreamingMessage(text.GREETINGS_TEXT)


@coreRouter.message(Command("profile"), F.chat.type == "private")
async def profile(message: types.Message, chat: types.Chat):
    subscription = SubscriptionManager.getChatCurrentSubscription(chatId=chat.id)
    userPlan = PlanManager.get(subscription.planId)
    limit = Limit.get(userPlan.limitId)
    currentGptModel = Chat.get(chat.id).currentGptModel

    try:
        activity = ChatActivity.getOrCreate(chat.id).to_dict()
        activity["stats"] = ChatActivityManager.getChatActivityStats(chatId=chat.id, limit=limit,
                                                                     subscription=subscription)
        chatActivityScheme = ChatActivityViewScheme(**activity)
        chatQuotaScheme = ChatQuotaGetScheme(**ChatQuota.getOrCreate(chat.id).to_dict())

        profileText = text.getProfileText(plantTitle=userPlan.title, chatActivityScheme=chatActivityScheme,
                                          chatQuotaScheme=chatQuotaScheme, currentGptModel=currentGptModel)

        return await message.answer(profileText, reply_markup=profileMarkup)

    except TelegramBadRequest as e:
        logger.exception("An error occured", exc_info=e.message)
        return message.reply(text.SERVER_ERROR_TRY_AGAIN)


@coreRouter.callback_query(F.data == "change_chat_gpt_model")
async def changeUserGptModel(callback: types.CallbackQuery, chat: types.Chat, state: FSMContext):
    await callback.answer("")
    await bot.send_message(chat.id, text.SELECT_GPT_MODEL, reply_markup=gptModelsMarkup)
    await state.set_state(ChooseGptModelState.model)


@coreRouter.message(ChooseGptModelState.model)
async def setUserGptModel(message: types.Message, state: FSMContext, chat: types.Chat):
    model = message.text
    availableModels = ["gpt-3.5-turbo-0125", "gpt-4"]
    subscription = SubscriptionManager.getChatCurrentSubscription(chatId=chat.id)
    userPlan = PlanManager.get(subscription.planId)
    limit = Limit.get(userPlan.limitId)

    if model not in availableModels:
        await state.clear()
        return message.answer("Notog'ri gpt model!")

    if model == "gpt-4" and limit.monthlyLimitGpt4 < 1:
        await state.clear()
        return await message.answer(text.UNAVAILABLE_GPT_MODEL)

    chatObj = Chat.get(chat.id)
    chatObj.currentGptModel = message.text
    chatObj.save()

    await state.clear()
    await message.answer(text.UPDATED_MODEL, reply_markup=ReplyKeyboardRemove())
    return await profile(message=message, chat=chat)


@coreRouter.message(Command("feedback"))
async def feedback(message: types.Message, chat: types.Chat):
    await bot.send_message(chat.id, text.REQUEST_FEEDBACK_MESSAGE, reply_markup=feedbackMarkup)


@coreRouter.callback_query(F.data == "feedback_callback")
async def feedbackCallback(callback: types.CallbackQuery, user: types.User, state: FSMContext):
    """ Feedback callback"""
    await callback.answer("")
    await bot.delete_message(user.id, callback.message.message_id)
    await bot.send_message(chat_id=user.id, text=text.FEEDBACK_GUIDE_MESSAGE,
                           reply_markup=cancelMarkup)

    await state.set_state(FeedbackMessageState.text)


@coreRouter.message(FeedbackMessageState.text)
async def setFeedbackMessage(message: types.Message, user: types.User, state: FSMContext):
    data = {**user.model_dump(), "text": message.text}
    await bot.send_message(settings.COMMENTS_GROUP_ID,
                           text.FEEDBACK_MESSAGE_EVENT_TEMPLATE.format_map(data))
    await state.clear()
    return await message.answer(text.THANK_YOU_TEXT)


@coreRouter.message(Command("help"))
async def helpCommand(message: types.Message):
    await message.answer(text.HELP_COMMAND)


@coreRouter.callback_query(F.data == "referral_link")
async def getReferralInfo(callback: types.CallbackQuery, user: types.User):
    await callback.answer("Referral!")
    await bot.send_message(user.id, text.REFERRAL_GUIDE.format(userId=user.id,
                                                               botUsername=settings.BOT_USERNAME))


@coreRouter.callback_query(F.data == "translate_callback")
async def translateCallback(callback: types.CallbackQuery, user: types.User):
    await callback.answer("")

    chatActivity = ChatActivity.getOrCreate(chatId=user.id)
    userSubscription = SubscriptionManager.getChatCurrentSubscription(chatId=user.id)
    plan = PlanManager.get(userSubscription.planId)
    limit = Limit.get(plan.limitId)

    if chatActivity.translatedMessagesCount >= limit.monthlyLimitTranslation:
        return await bot.send_message(chat_id=user.id, text=text.LIMIT_TRANSLATION_REACHED)

    ChatActivityManager.incrementActivityCount(user.id, "translatedMessagesCount")
    translatedMessage = translateMessage(callback.message.text, "auto",
                                         "uz", isTranslate=True)

    await bot.edit_message_text(chat_id=user.id, message_id=callback.message.message_id,
                                text=translatedMessage)


# Callbacks for feeedback cancelation
@coreRouter.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, user: types.User, state: FSMContext):
    try:
        await bot.delete_message(user.id, callback.message.message_id)
    except TelegramNotFound as e:
        logger.exception("An error occured", exc_info=e.message)

    await callback.answer(text.CANCELED_TEXT)
    await state.clear()


@coreRouter.message(Command("new"))
async def newChat(message: types.Message, chat: types.Chat):
    MessageManager.clearUserChat(chat.id)
    await bot.send_message(chat.id, text.CONTEXT_CHAT_CLEARED_TEXT)


@coreRouter.message(F.text == "Bekor qilish")
async def cancelButton(message: types.Message, state: FSMContext):
    await state.clear()
    return await bot.send_message(message.chat.id, text.CANCELED_TEXT, reply_markup=types.ReplyKeyboardRemove())


@coreRouter.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def onUserJoin(event: ChatMemberUpdated):
    return await bot.send_message(event.chat.id, text.NEW_CHAT_MEMBER_TEMPLATE.format(
        firstName=event.from_user.first_name))


@coreRouter.message(isBotMentioned(), TextContentFilter())
@coreRouter.message(TextContentFilter())
async def handleMessages(message: types.Message, chat: types.Chat):
    try:
        progressMessage = await bot.send_message(chat_id=chat.id, text=text.WAIT_MESSAGE_TEXT)

        async with ChatActionSender.typing(bot=bot, chat_id=chat.id):
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
