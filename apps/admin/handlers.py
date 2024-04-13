from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot
from db.state import AdminLoginState, AdminSystemMessageState, SendMessageWithInlineState,  AdminSendMessage, TopupState, RejectState
from utils.message import fetchUsersByType, SendAny
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from apps.core.models import ChatActivity, Message
from .keyboards import adminKeyboardsMarkup, cancelKeyboardsMarkup, sendMessageMarkup, getInlineMenu
from utils import extractInlineButtons, text
from utils.events import sendError
from filters.bound_filters import IsAdmin
from filters.permission import checkPassword
from apps.subscription.managers import SubscriptionManager, PlanManager
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

adminRouter = Router(name="adminRouter")


@adminRouter.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):   
    await state.clear()

    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.chat.id, "State bekor qilindi!", reply_markup=adminKeyboardsMarkup)
    
    return await bot.send_message(message.chat.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


@adminRouter.message(Command('admin'))
async def admin(message: types.Message, state: FSMContext):
    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!",
                                      reply_markup=adminKeyboardsMarkup)

    await state.set_state(AdminLoginState.password)
    return await message.answer("Parolni kiriting!")


@adminRouter.message(AdminLoginState.password)
async def passwordHandler(message: types.Message, state: FSMContext):
    user = message.from_user

    await state.update_data(password=message.text)

    if checkPassword(message.text):
        await state.clear()
        Admin(user.id).register(user.id)
        return await bot.send_message(user.id, "Xush kelibsiz admin!", reply_markup=adminKeyboardsMarkup)
    
    return await message.answer("Noto'g'ri parol!")


@adminRouter.message(IsAdmin(), F.text == "🤖 System xabar yuborish.!")
async def sendRuleMessage(message: types.Message):
    await AdminSystemMessageState.message.set()
    return await message.answer(
        "Qoidani faqat ingliz yoki rus tilida kiriting!", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), AdminSystemMessageState.message)
async def addRule(message: types.Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.clear()
    MessageManager.systemToAllChat(text=message.text)
    return await message.answer("System xabar kiritildi!")


@adminRouter.message(IsAdmin(), F.text == "📊 Statistika.!")
async def getStatistics(message: types.Message):
    usersCount = ChatManager.usersCount()
    allMessages = Message.count()
    avgUsersMessagesCount = allMessages / usersCount

    return await message.answer(text.getStatisticsText(
        usersCount=usersCount,
        activeUsers=ChatActivityManager.getCurrentMonthUsers(),
        activeUsersOfDay=ChatActivityManager.getTodayActiveUsers(),
        usersUsedOneDay=ChatActivityManager.getUsersUsedOneDay(),
        usersUsedOneWeek=ChatActivityManager.getUsersUsedOneWeek(),
        usersUsedOneMonth=ChatActivityManager.getUsersUsedOneMonth(),
        premiumUsers=SubscriptionManager.getPremiumUsersCount(),
        limitReachedUsers=ChatActivityManager.getLimitReachedUsers(),
        allMessages=allMessages,
        avgUsersMessagesCount=avgUsersMessagesCount,
        todayMessages=MessageManager.getTodayMessagesCount(),
        lastUpdate=ChatActivityManager.getLatestChat().lastUpdated,
        latestUser=ChatActivityManager.getLatestChat().chatId
    ))


# Subscription handlers
@adminRouter.message(IsAdmin(), F.text == "🎁 Premium obuna.!")
async def giveSubscription(message: types.Message, state: FSMContext):
    await state.set_state(TopupState.chatId)
    return await message.answer("Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), TopupState.chatId)
async def topUpSetChatId(message: types.Message, state: FSMContext):
    await state.update_data(chatId=message.text)

    unPaidPremiumSubscription = SubscriptionManager.getUnpaidPremiumSubscription(
        chatId=message.text, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    if not unPaidPremiumSubscription:
        await state.clear()
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")
    
    await state.set_state(TopupState.sure)
    return await message.answer(
        "Siz rostan ushbu userga premium obuna taqdim etmoqchimisiz? Xa/Yo'q",
        reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), TopupState.sure)
async def subscribeUser(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chatId = data.get("chatId")

    if message.text != "Xa":
        await state.clear()
        return await message.answer("Bekor qilindi!", reply_markup=adminKeyboardsMarkup)
    
    SubscriptionManager.unsubscribe(
        PlanManager.getFreePlanOrCreate().id,
        chatId=chatId
    )
    
    chatActivity = ChatActivity.getOrCreate(chatId=chatId)
    ChatActivity.update(chatActivity, "todaysMessages", 1)

    SubscriptionManager.subscribe(
        chatId=chatId, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    await bot.send_message(chatId, text.PREMIUM_GRANTED_TEXT)
    
    await state.clear()
    return await message.answer("Ushbu foydalanuvchi premium obunaga ega bo'ldi 🎉", reply_markup=adminKeyboardsMarkup)


@adminRouter.message(IsAdmin(), F.text == "✖️ Premiumni rad etish.!")
async def cancelSubscription(message: types.Message, state: FSMContext):
    await state.set_state(RejectState.chatId)
    return await message.answer("Chat id kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.chatId)
async def setChatIdReject(message: types.Message, state: FSMContext):
    await state.update_data(chatId=message.text)
    await state.set_state(RejectState.reason)
    return await message.answer("Sababni kiriting", reply_markup=cancelKeyboardsMarkup)


@adminRouter.message(IsAdmin(), RejectState.reason)
async def rejectReason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chatId = data.get("chatId")

    try:
        await bot.send_message(chatId, text.getRejectReason(message.text))
    except TelegramBadRequest:
        print("Bot blocked!")

    SubscriptionManager.rejectPremiumRequest(chatId)
    
    await state.clear()
    return await message.answer("Premium obuna rad etildi", reply_markup=adminKeyboardsMarkup)


# Send Message command

@adminRouter.message(IsAdmin(), F.text == "📤 Xabar yuborish.!")
async def sendMessageToUsers(message: types.Message):
    return await message.answer(
        "Xabar turini kiriting", reply_markup=sendMessageMarkup)


""" Handling the send message command"""


# Handlers of send message with inline buttons
@adminRouter.callback_query(F.data == "without_inline")
async def setUserTypeToSend(message: types.Message, state: FSMContext):
    await state.set_state(AdminSendMessage.userType)
    await bot.send_message(message.from_user.id, "Kimlarga yuborishni tanlang, FREE/ALL")
    return await message.answer("Kimlarga yuborishni tanlang, FREE/ALL")


@adminRouter.message(AdminSendMessage.userType)
async def setMessage(message: types.Message, state: FSMContext):
    await state.update_data(contentType=message.text)
    await bot.send_message(message.from_user.id, "Xabar/Rasm/Video kiriting")
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
async def checkIsSubscribed_Inline(message: types.Message, state: FSMContext):
    await state.set_state(SendMessageWithInlineState.buttons)
    await bot.send_message(message.from_user.id,
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

