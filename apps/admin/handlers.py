from aiogram.dispatcher import FSMContext
from bot import dp, types, bot
from db.state import AdminLoginState, AdminSystemMessageState, SendMessageWithInlineState,  AdminSendMessage, TopupState, RejectState
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from apps.core.models import ChatActivity, Message
from .keyboards import adminKeyboards, cancelKeyboards, sendMessageMenu, getInlineMenu
from aiogram.dispatcher.filters import Text
from utils import SendAny, extractInlineButtons, constants, text, sendError
from filters.core import IsAdmin, checkPassword
from apps.subscription.managers import SubscriptionManager, PlanManager
from aiogram.utils.exceptions import BotBlocked
import asyncio


@dp.message_handler(commands=["cancel"], state='*')
async def cancel(message: types.Message, state: FSMContext):   
    await state.finish()
    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.chat.id, "State bekor qilindi!", reply_markup=adminKeyboards)
    
    return await bot.send_message(message.chat.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!",
                                      reply_markup=adminKeyboards)

    await AdminLoginState.password.set()
    return await message.answer("Parolni kiriting!")


@dp.message_handler(state=AdminLoginState.password)
async def password_handler(message: types.Message, state=FSMContext):
    user = message.from_user
    async with state.proxy() as data:
        data['password'] = message.text

    if checkPassword(message.text):
        await state.finish()
        Admin(user.id).register(user.id)
        return await bot.send_message(user.id, "Xush kelibsiz admin!", reply_markup=adminKeyboards)
    
    return await message.answer("Noto'g'ri parol!")


@dp.message_handler(IsAdmin(), Text(equals="🤖 System xabar yuborish.!"))
async def sendRuleMessage(message: types.Message):
    await AdminSystemMessageState.message.set()
    return await message.answer(
        "Qoidani faqat ingliz yoki rus tilida kiriting!", reply_markup=cancelKeyboards)
    

@dp.message_handler(IsAdmin(), state=AdminSystemMessageState.message)
async def addRule(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text

    await state.finish()
    MessageManager.systemToAllChat(text=message.text)
    return await message.answer("System xabar kiritildi!")


@dp.message_handler(IsAdmin(), Text(equals="📊 Statistika.!"))
async def getStatistics(message: types.Message):
    usersCount = ChatManager.usersCount()
    allMessages = Message.count()
    avgUsersMessagesCount = allMessages / usersCount

    return await message.answer(text.getStatisticsText(
        usersCount,
        ChatManager.activeMonthlyUsers(),
        ChatManager.activeDailyUsers(),
        SubscriptionManager.getPremiumUsersCount(),
        ChatActivityManager.getLimitReachedUsers(),
        allMessages,
        avgUsersMessagesCount
    ))


@dp.message_handler(IsAdmin(), Text(equals="📤 Xabar yuborish.!"))
async def sendMessageToUsers(message: types.Message):
    return await message.answer(
        "Xabar turini kiriting", reply_markup=sendMessageMenu)


# Subscribe user

@dp.message_handler(IsAdmin(), Text(equals="🎁 Premium obuna.!"))
async def giveSubscription(message: types.Message):
    await TopupState.chatId.set()
    return await message.answer("Chat id kiriting", reply_markup=cancelKeyboards)


@dp.message_handler(IsAdmin(), state=TopupState.chatId)
async def topUpSetChatId(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['chatId'] = message.text

    premium_subscription = SubscriptionManager.getNotPaidPremiumSubscription(
        chatId=message.text, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    if premium_subscription is None:
        await state.finish()
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")
    
    await TopupState.next()
    return await message.answer(
        "Siz rostan ushbu userga premium obuna taqdim etmoqchimisiz? Xa/Yo'q",
        reply_markup=cancelKeyboards)


@dp.message_handler(IsAdmin(), state=TopupState.sure)
async def subscribeUser(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        chatId = data['chatId']

    if message.text != "Xa":
        await state.finish()
        return await message.answer("Bekor qilindi!", reply_markup=adminKeyboards)
    
    SubscriptionManager.unsubscribe(
        PlanManager.getFreePlanOrCreate().id,
        chatId=chatId
    )
    
    chatActivity = ChatActivity.get(chatId=chatId)
    ChatActivity.update(chatActivity, "todaysMessages", 20 - chatActivity.todaysMessages)

    SubscriptionManager.subscribe(
        chatId=chatId, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    await bot.send_message(chatId, text.PREMIUM_GAVE)
    
    await state.finish()
    return await message.answer("Ushbu foydalanuvchi premium obunaga ega bo'ldi 🎉", reply_markup=adminKeyboards)


@dp.message_handler(IsAdmin(), Text(equals="✖️ Premiumni rad etish.!"))
async def cancelSubscription(message: types.Message):
    await RejectState.chatId.set()
    return await message.answer("Chat id kiriting", reply_markup=cancelKeyboards)


@dp.message_handler(IsAdmin(), state=RejectState.chatId)
async def setChatIdReject(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['chatId'] = message.text

    await RejectState.next()
    return await message.answer("Sababni kiriting", reply_markup=cancelKeyboards)


@dp.message_handler(IsAdmin(), state=RejectState.reason)
async def rejectReason(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        chatId = data['chatId']

    try:
        await bot.send_message(chatId, text.getRejectReason(message.text))
    except BotBlocked:
        print("Bot blocked!")

    SubscriptionManager.rejectPremiumRequest(chatId)
    
    await state.finish()
    return await message.answer("Premium obuna rad etildi", reply_markup=adminKeyboards)


# Callback with and without inline
@dp.callback_query_handler(text="without_inline")
async def checkIsSubscribed(message: types.Message):
    await AdminSendMessage.contentType.set()
    await bot.send_message(message.from_user.id, "Kimlarga yuborishni tanlang, FREE/ALL")
    return await message.answer("Kimlarga yuborishni tanlang, FREE/ALL")


#  todo: extract method to another file

def fetchUsersByType(contentType):
    if contentType == "FREE":
        users = PlanManager.getFreePlanUsers()
    elif contentType == "ALL":
        users = ChatManager.all()
    else:
        return False

    return users


async def sendAnyMessages(users, message, inlineKeyboards=None):
    sendAny = SendAny(message)

    async def process_user(user):
        try:
            contentTypeHandlers = {
                "text": sendAny.sendMessage,
                "photo": sendAny.sendPhoto,
                "video": sendAny.sendVideo,
                "animation": sendAny.sendAnimation
            }

            content_type = message.content_type
            handler = contentTypeHandlers.get(content_type)

            if handler:
                await handler(chatId=user.chatId, kb=inlineKeyboards)

        except Exception as e:
            return 0

    tasks = [process_user(user) for user in users]
    blockedUsersCount = await asyncio.gather(*tasks)

    return blockedUsersCount


@dp.message_handler(state=AdminSendMessage.contentType)
async def setContentType(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["contentType"] = message.text

    await bot.send_message(message.from_user.id, "Xabar/Rasm/Video kiriting")
    await AdminSendMessage.next()


@dp.message_handler(state=AdminSendMessage.message, content_types=types.ContentType.ANY)
async def sendToUsersMessage(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        contentType = data["contentType"]

    users = fetchUsersByType(contentType)

    if not users:
        await state.finish()
        return await message.answer("Bekor qilindi!", reply_markup=adminKeyboards)

    blockedUsersCount = sendAnyMessages(users, message)

    await sendError(f"Bot was blocked by {blockedUsersCount} users")
    await state.finish()

    return await message.answer("Xabar yuborildi!")


# With inline buttons set
@dp.message_handler(state=SendMessageWithInlineState.buttons)
async def setButtons(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["buttons"] = message.text
    
    await SendMessageWithInlineState.next()
    return await message.answer("Xabar/Rasm/Video kiriting")


# Callback the inline button
@dp.callback_query_handler(text="with_inline")
async def checkIsSubscribed_Inline(message: types.Message):
    await SendMessageWithInlineState.buttons.set()

    await bot.send_message(message.from_user.id,
                           text.INLINE_BUTTONS_GUIDE, parse_mode='MARKDOWN')
    return await message.answer("Inline")


# Send message with inline buttons
@dp.message_handler(state=SendMessageWithInlineState.message, content_types=types.ContentType.ANY)
async def sendMessageWithInline(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        inlineKeyboardsText = data["buttons"]

    inlineKeyboards = extractInlineButtons(inlineKeyboardsText)

    users = PlanManager.getFreePlanUsers()
    blockedUsersCount = sendAnyMessages(users, message,
                                        getInlineMenu(inlineKeyboards))

    await sendError(f"Bot was blocked by {blockedUsersCount} users")
    await state.finish()

    return await message.answer("Xabar yuborildi!")

