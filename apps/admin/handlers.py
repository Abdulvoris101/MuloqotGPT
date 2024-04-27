import uuid

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot, logger
from db.state import AdminLoginState, SendMessageToUsers, ConfirmSubscriptionState, RejectState
from apps.common.exception import AiogramException
from utils.message import fetchUsersByUserType, SendAny
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from apps.core.models import Message
from .keyboards import (adminKeyboardsMarkup, cancelKeyboardsMarkup,
                        sendMessageMarkup, getInlineMarkup, confirmSubscriptionMarkup)
from utils import extractInlineButtonsFromText, text
from apps.admin.events import sendError
from apps.common.filters.bound_filters import IsAdmin
from apps.common.filters.permission import checkPassword
from apps.subscription.managers import SubscriptionManager, PlanManager
from aiogram.exceptions import TelegramBadRequest

from .schemes import StatisticsReadScheme

adminRouter = Router(name="adminRouter")


@adminRouter.message(Command("cancel"))
async def cancel(message: types.Message, user: types.User, state: FSMContext):
    await state.clear()
    if Admin.isAdmin(user.id):
        return await bot.send_message(user.id, text.CANCELED_TEXT, reply_markup=adminKeyboardsMarkup)
    return await bot.send_message(user.id, text.CANCELED_TEXT, reply_markup=types.ReplyKeyboardRemove())


@adminRouter.message(Command('admin'))
async def adminHandler(message: types.Message, user: types.User, state: FSMContext):
    if Admin.isAdmin(user.id):
        return await bot.send_message(user.id, "Xush kelibsiz admin!",
                                      reply_markup=adminKeyboardsMarkup)

    await state.set_state(AdminLoginState.password)
    return await message.answer("Parolni kiriting!")


@adminRouter.message(AdminLoginState.password)
async def adminLogin(message: types.Message, user: types.User, state: FSMContext):
    await state.update_data(password=message.text)
    if checkPassword(password=message.text):
        await state.clear()

        Admin(user.id).register()
        return await bot.send_message(user.id, "Xush kelibsiz admin!", reply_markup=adminKeyboardsMarkup)
    
    return await message.answer("Noto'g'ri parol!")


#  Statistics

@adminRouter.callback_query(IsAdmin(), F.data == "statistics")
async def statisticsHandler(callback: types.CallbackQuery, chat: types.Chat):
    await callback.answer("")

    usersCount = ChatManager.usersCount()
    allMessages = Message.count()
    avgUsersMessagesCount = allMessages / usersCount
    lastChat = ChatActivityManager.getLatestChat()

    scheme = StatisticsReadScheme(
        usersCount=usersCount,
        activeUsers=ChatActivityManager.getCurrentMonthUsers(),
        activeUsersOfDay=ChatActivityManager.getUserActivityTimeFrame(days=1),
        usersUsedOneDay=ChatActivityManager.getActiveUsersTimeFrame(days=1),
        usersUsedOneWeek=ChatActivityManager.getActiveUsersTimeFrame(days=7),
        usersUsedOneMonth=ChatActivityManager.getActiveUsersTimeFrame(days=30),
        premiumUsers=SubscriptionManager.getPremiumUsersCount(),
        allMessages=allMessages,
        avgUsersMessagesCount=avgUsersMessagesCount,
        todayMessages=MessageManager.getMessagesActivityTimeFrame(days=1, messageType='message'),
        lastUpdate=lastChat.lastUpdated,
        latestUserId=lastChat.chatId
    )
    data = scheme.model_dump()
    return await bot.send_message(chat.id, text.STATISTICS_TEXT.format_map(data))


# Subscription grant handlers
@adminRouter.callback_query(IsAdmin(), F.data == "give_premium")
async def premiumGrant(callback: types.CallbackQuery, chat: types.Chat, state: FSMContext):
    try:
        await callback.answer("")
    except TelegramBadRequest as e:
        logger.error("An error occured", str(e.message))

    await state.set_state(ConfirmSubscriptionState.receiverId)
    return await bot.send_message(chat.id, "Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(ConfirmSubscriptionState.receiverId)
async def enterReceiverId(message: types.Message, state: FSMContext):
    try:
        receiverId = int(message.text)
    except ValueError:
        await state.clear()
        return await bot.send_message(message.chat.id, text.CANCELED_TEXT, reply_markup=cancelKeyboardsMarkup)

    await state.update_data(receiverId=receiverId)
    await state.set_state(ConfirmSubscriptionState.planId)
    return await message.answer("Plan id kiriting")


@adminRouter.message(ConfirmSubscriptionState.planId)
async def processPremiumRequest(message: types.Message, state: FSMContext):
    try:
        planId = uuid.UUID(message.text)
    except ValueError:
        await state.clear()
        return await bot.send_message(message.chat.id, text.CANCELED_TEXT,
                                      reply_markup=cancelKeyboardsMarkup)

    data = await state.get_data()
    receiverId = data.get("receiverId")

    if not PlanManager.isExistsById(planId=planId):
        return message.answer("Plan mavjud emas!")

    unPaidPremiumSubscription = SubscriptionManager.getInActiveSubscription(
        chatId=int(receiverId), planId=planId)

    if not unPaidPremiumSubscription:
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")

    await state.update_data(planId=str(planId))

    return await message.answer(text.SURE_TO_SUBSCRIBE, reply_markup=confirmSubscriptionMarkup)


@adminRouter.callback_query(IsAdmin(), F.data == "subscribe_yes")
async def finalizeSubscription(query: types.CallbackQuery, state: FSMContext):
    await query.answer("")

    data = await state.get_data()
    receiverId = data.get("receiverId")
    planId = data.get("planId")

    SubscriptionManager.bulkUnsubscribe(plans=PlanManager.excludePlan(planId=planId),
                                        chatId=receiverId)
    SubscriptionManager.subscribe(chatId=receiverId, planId=planId)

    await bot.send_message(receiverId, text.PREMIUM_GRANTED_TEXT)
    await state.clear()
    return await bot.send_message(query.from_user.id, text.SUCCESSFULLY_SUBSCRIBED,
                                  reply_markup=adminKeyboardsMarkup)


# Reject subscription handler
@adminRouter.callback_query(IsAdmin(), F.data == "reject_subscription_request")
async def rejectSubscriptionRequest(callback: types.Message, chat: types.Chat, state: FSMContext):
    await callback.answer("")
    await state.set_state(RejectState.receiverId)
    return await bot.send_message(chat.id, "Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.receiverId)
async def setRejectionReceiverId(message: types.Message, state: FSMContext):
    if not ChatManager.isExistsByUserId(chatId=int(message.text)):
        return await message.answer(text.NOT_FOUND_USER)

    await state.update_data(receiverId=message.text)
    await state.set_state(RejectState.reason)
    return await message.answer("Sababni kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.reason)
async def processRejectionReason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    receiverId = data.get("receiverId")

    try:
        SubscriptionManager.rejectPremiumRequest(receiverId)
        await bot.send_message(receiverId, text.REJECTED_TEXT.format(reason=message.text))
    except TelegramBadRequest:
        await bot.send_message(message.chat.id, "Bot foydalanuvchi tomonidan bloklangan")
    except AiogramException as e:
        return await bot.send_message(message.chat.id, e.message_text)

    await state.clear()
    return await message.answer("Premium obuna rad etildi", reply_markup=adminKeyboardsMarkup)


# Send Message command


@adminRouter.callback_query(IsAdmin(), F.data == "send_message_to_users")
async def initiateMessageSending(callback: types.CallbackQuery, chat: types.Chat, state: FSMContext):
    await callback.answer("")
    await state.set_state(SendMessageToUsers.messageType)
    return await bot.send_message(chat.id, "Xabar turini kiriting",
                                  reply_markup=sendMessageMarkup)


@adminRouter.message(SendMessageToUsers.messageType)
async def selectMessageType(message: types.Message, user: types.User, state: FSMContext):
    await state.update_data(messageType=message.text)
    await state.set_state(SendMessageToUsers.userType)
    await bot.send_message(user.id, "Kimlarga yuborishni tanlang, FREE/ALL")


@adminRouter.message(SendMessageToUsers.userType)
async def selectUserSegment(message: types.Message, user: types.User, state: FSMContext):
    await state.update_data(userType=message.text)
    data = await state.get_data()

    if data.get("messageType") == "Inline bilan":
        await state.set_state(SendMessageToUsers.buttons)
        await bot.send_message(user.id, text.INLINE_BUTTONS_GUIDE)
        return

    await state.set_state(SendMessageToUsers.message)
    await bot.send_message(user.id, text.SELECT_MESSAGE_TYPE)


@adminRouter.message(SendMessageToUsers.buttons)
async def setInlineButtons(message: types.Message, state: FSMContext):
    await state.update_data(buttons=message.text)
    await state.set_state(SendMessageToUsers.message)
    return await message.answer(text.SELECT_MESSAGE_TYPE)


@adminRouter.message(SendMessageToUsers.message)
async def sendMessageToUsers(message: types.Message, state: FSMContext):
    data = await state.get_data()

    chats = fetchUsersByUserType(userType=data.get("userType"))
    sendAny = SendAny(message=message)

    if data.get("messageType") == "Inline bilan":
        inlineButtons = extractInlineButtonsFromText(data.get("buttons"))
        reportData = await sendAny.sendAnyMessages(
            chats=chats, reply_markup=getInlineMarkup(inlineButtons))
    else:
        reportData = await sendAny.sendAnyMessages(chats)

    await sendError(text.SENT_USER_REPORT_TEXT.format(
        receivedUsersCount=reportData.get("receivedUsersCount"),
        blockedUsersCount=reportData.get("blockedUsersCount"))
    )

    await state.clear()

    return await message.answer("Xabar yuborildi!")


