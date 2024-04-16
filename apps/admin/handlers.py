from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot
from db.state import AdminLoginState, SendMessageWithInlineState,  AdminSendMessage, ConfirmSubscriptionState, RejectState
from utils.exception import AiogramException
from utils.message import fetchUsersByType, SendAny
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from apps.core.models import ChatActivity, Message

from .keyboards import (adminKeyboardsMarkup, cancelKeyboardsMarkup,
                        sendMessageMarkup, getInlineMenu, getConfirmSubscriptionMarkup,
                        ConfirmSubscriptionCallback)

from utils import extractInlineButtons, text
from utils.events import sendError
from filters.bound_filters import IsAdmin
from filters.permission import checkPassword
from apps.subscription.managers import SubscriptionManager, PlanManager
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from .schemes import StatisticsReadScheme

adminRouter = Router(name="adminRouter")


@adminRouter.message(Command("cancel"))
async def cancel(message: types.Message, user: types.User, state: FSMContext):
    await state.clear()
    if Admin.isAdmin(user.id):
        return await bot.send_message(user.id, "State bekor qilindi!", reply_markup=adminKeyboardsMarkup)
    return await bot.send_message(user.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


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
        activeUsersOfDay=ChatActivityManager.getTodayActiveUsers(),
        usersUsedOneDay=ChatActivityManager.getUserActivityTimeFrame(days=1),
        usersUsedOneWeek=ChatActivityManager.getUserActivityTimeFrame(days=7),
        usersUsedOneMonth=ChatActivityManager.getUserActivityTimeFrame(days=30),
        premiumUsers=SubscriptionManager.getPremiumUsersCount(),
        limitReachedUsers=ChatActivityManager.getLimitReachedUsers(),
        allMessages=allMessages,
        avgUsersMessagesCount=avgUsersMessagesCount,
        todayMessages=MessageManager.getTodayMessagesCount(),
        lastUpdate=lastChat.lastUpdated,
        latestUserId=lastChat.chatId
    )
    data = scheme.model_dump()
    return await bot.send_message(chat.id, text.STATISTICS_TEXT.format_map(data))


# Subscription handlers
@adminRouter.callback_query(IsAdmin(), F.data == "give_premium")
async def premiumGrant(callback: types.CallbackQuery, chat: types.Chat, state: FSMContext):
    await callback.answer("")
    await state.set_state(ConfirmSubscriptionState.receiverId)
    return await bot.send_message(chat.id, "Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(ConfirmSubscriptionState.receiverId)
async def processPremiumRequest(message: types.Message, state: FSMContext):
    await state.update_data(receiverId=message.text)

    unPaidPremiumSubscription = SubscriptionManager.getInActiveSubscription(
        chatId=message.chat.id, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    if not unPaidPremiumSubscription:
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")

    await state.clear()
    return await message.answer(
        "Siz rostan ushbu foydalanuvchiga premium obuna taqdim etmoqchimisiz?",
        reply_markup=getConfirmSubscriptionMarkup(receiverId=int(message.text)))


@adminRouter.message(IsAdmin(), ConfirmSubscriptionCallback.filter(F.name == "subscribe_yes"))
async def finalizeSubscription(message: types.Message, callbackData: ConfirmSubscriptionCallback):
    receiverId = callbackData.receiverId
    SubscriptionManager.unsubscribe(PlanManager.getFreePlanOrCreate().id, chatId=receiverId)
    chatActivity = ChatActivity.getOrCreate(chatId=receiverId)
    ChatActivity.update(chatActivity, "todaysMessages", 1)
    SubscriptionManager.subscribe(chatId=receiverId, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    await bot.send_message(receiverId, text.PREMIUM_GRANTED_TEXT)
    return await message.answer("Ushbu foydalanuvchi premium obunaga ega bo'ldi 🎉",
                                reply_markup=adminKeyboardsMarkup)


@adminRouter.callback_query(IsAdmin(), F.data == "reject_subscription_request")
async def rejectSubscriptionRequest(callback: types.Message, chat: types.Chat, state: FSMContext):
    await callback.answer("")
    await state.set_state(RejectState.receiverId)
    return await bot.send_message(chat.id, "Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.receiverId)
async def setRejectionReceiverId(message: types.Message, state: FSMContext):
    await state.update_data(receiverId=message.text)
    await state.set_state(RejectState.reason)
    return await message.answer("Sababni kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.reason)
async def processRejectionReason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    receiverId = data.get("receiverId")

    try:
        SubscriptionManager.rejectPremiumRequest(receiverId)
        await bot.send_message(receiverId, text.getRejectReason(message.text))
    except TelegramBadRequest:
        await bot.send_message(message.chat.id, "Bot foydalanuvchi tomonidan bloklangan")
    except AiogramException as e:
        return await bot.send_message(message.chat.id, e.message_text)

    await state.clear()
    return await message.answer("Premium obuna rad etildi", reply_markup=adminKeyboardsMarkup)


# Send Message command

@adminRouter.callback_query(IsAdmin(), F.data == "send_message_to_users")
async def sendMessageToUsers(callback: types.CallbackQuery, chat: types.Chat):
    await callback.answer("")
    return await bot.send_message(chat.id, "Xabar turini kiriting", reply_markup=sendMessageMarkup)


""" Handling the send message command"""


# Handlers of send message with inline buttons
@adminRouter.callback_query(F.data == "without_inline")
async def setUserTypeToSend(message: types.Message, user: types.User, state: FSMContext):
    await state.set_state(AdminSendMessage.userType)
    await bot.send_message(user.id, "Kimlarga yuborishni tanlang, FREE/ALL")
    return await message.answer("Kimlarga yuborishni tanlang, FREE/ALL")


@adminRouter.message(AdminSendMessage.userType)
async def setMessage(message: types.Message, user: types.User, state: FSMContext):
    await state.update_data(contentType=message.text)
    await bot.send_message(user.id, "Xabar/Rasm/Video kiriting")
    await state.set_state(AdminSendMessage.message)


@adminRouter.message(AdminSendMessage.message, F.ANY)
async def sendToUsersMessage(message: types.Message, state: FSMContext):
    data = await state.get_data()
    contentType = data.get("contentType")

    users = fetchUsersByType(contentType)

    if not users:
        await state.clear()
        return await message.answer("Foydalanuvchilar yo'q!", reply_markup=adminKeyboardsMarkup)

    receivedUsersCount, blockedUsersCount = await SendAny(message=message).sendAnyMessages(users)

    await sendError(f"Message sent to {receivedUsersCount} users")
    await sendError(f"Bot was blocked by {blockedUsersCount} users")

    await state.clear()

    return await message.answer("Xabar yuborildi!")


""" Send message with inline buttons handlers """


@adminRouter.callback_query(F.data == "with_inline")
async def checkIsSubscribed_Inline(message: types.Message, user: types.User, state: FSMContext):
    await state.set_state(SendMessageWithInlineState.buttons)
    await bot.send_message(user.id,
                           text.INLINE_BUTTONS_GUIDE, parse_mode='MARKDOWN')
    return await message.answer("Inline")


# Set inline buttons
@adminRouter.message(SendMessageWithInlineState.buttons)
async def setButtons(message: types.Message, state: FSMContext):
    await state.update_data(buttons=message.text)
    await state.set_state(SendMessageWithInlineState.message)

    return await message.answer("Xabar/Rasm/Video kiriting")


@adminRouter.message(SendMessageWithInlineState.message, F.Any)
async def sendMessageWithInline(message: types.Message, state: FSMContext):
    data = await state.get_data()

    inlineKeyboardsText = data.get("buttons")
    inlineKeyboards = extractInlineButtons(inlineKeyboardsText)

    users = PlanManager.getFreePlanUsers()

    receivedUsersCount, blockedUsersCount = await SendAny(message=message).sendAnyMessages(
        users=users, inlineKeyboards=getInlineMenu(inlineKeyboards))

    await sendError(f"Message sent to {receivedUsersCount} users")
    await sendError(f"Bot was blocked by {blockedUsersCount} users")
    await state.clear()

    return await message.answer("Xabar yuborildi!")

