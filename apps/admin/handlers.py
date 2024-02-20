from aiogram.dispatcher import FSMContext
import os
from bot import dp, types, bot
from db.state import AdminLoginState, AdminSystemMessageState, SendMessageWithInlineState,  AdminSendMessage, TopupState, RejectState
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from apps.core.models import ChatActivity, Message
from .keyboards import adminKeyboards, cancelKeyboards, sendMessageMenu, dynamic_sendMenu
from aiogram.dispatcher.filters import Text
from utils import SendAny, extract_inline_buttons, constants, text, sendError
from filters.core import IsAdmin
from apps.subscription.managers import SubscriptionManager, PlanManager
from aiogram.utils.exceptions import BotBlocked

@dp.message_handler(commands=["cancel"], state='*')
async def cancel(message: types.Message, state: FSMContext):   
    await state.finish()
    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.chat.id, "State bekor qilindi!", reply_markup=adminKeyboards)
    
    return await bot.send_message(message.chat.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state=None):
    if Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!", reply_markup=adminKeyboards)
 
    await AdminLoginState.password.set()
    return await message.answer("Password kiriting!")


@dp.message_handler(state=AdminLoginState.password)
async def password_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    if message.text == str(constants.PASSWORD):
        await state.finish()
        Admin(message.from_user.id).register(message.from_user.id)
        
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!", reply_markup=adminKeyboards)
    
    return await message.answer("Noto'g'ri parol!")


@dp.message_handler(IsAdmin(), Text(equals="🤖 System xabar yuborish.!"))
async def add_rule_command(message: types.Message, state=None):        
    await AdminSystemMessageState.message.set()

    return await message.answer("Qoidani faqat ingliz yoki rus tilida kiriting!", reply_markup=cancelKeyboards)
    

@dp.message_handler(IsAdmin(), state=AdminSystemMessageState.message)
async def add_rule(message: types.Message, state=FSMContext):    
    async with state.proxy() as data:
        data['message'] = message.text

    await state.finish()
    
    MessageManager.systemToAllChat(text=message.text)
    return await message.answer("System xabar kiritildi!")



@dp.message_handler(IsAdmin(), Text(equals="📊 Statistika.!"))
async def get_statistics(message: types.Message):
    premiumUsers = SubscriptionManager.getPremiumUsersCount()
    usersCount = ChatManager.usersCount()
    activeUsers = ChatManager.activeMonthlyUsers()
    activeUsersOfDay = ChatManager.activeDailyUsers()
    allMessages = Message.count()
    avgUsersMessagesCount = allMessages / usersCount
    limitReachedUsers = ChatActivityManager.getLimitReachedUsers()
    
    return await message.answer(f"""👤 Foydalanuvchilar - {usersCount}
💥 Aktiv Foydalanuvchilar - {activeUsers}
💯 Kunlik Aktiv Foydalanuvchilar - {activeUsersOfDay}
🎁 Premium Foydalanuvchilar - {premiumUsers}
🛑 Bugungi limiti tugagan Foydalanuvchilar - {limitReachedUsers}
📨 Xabarlar - {allMessages}
📩 User uchun o'rtacha xabar - {avgUsersMessagesCount}""")


@dp.message_handler(IsAdmin(), Text(equals="📤 Xabar yuborish.!"))
async def sendMessageCommand(message: types.Message, state=None):
    return await message.answer("Xabarni turini kiriting", reply_markup=sendMessageMenu)


# Subscribe

@dp.message_handler(IsAdmin(), Text(equals="🎁 Premium obuna.!"))
async def subscribeUser(message: types.Message):
    await TopupState.chatId.set()
    return await message.answer("Chat id kiriting", reply_markup=cancelKeyboards)


@dp.message_handler(IsAdmin(), state=TopupState.chatId)
async def setChaId(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        data['chatId'] = message.text

    premium_subscription = SubscriptionManager.getNotPaidPremiumSubscription(
        chatId=message.text, planId=PlanManager.getPremiumPlanOrCreate().id)
    
    if premium_subscription is None:
        await state.finish()
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")
    
    await TopupState.next()
    return await message.answer("Siz rostan ushbu userga premium obuna taqdim etmoqchimisiz? Xa/Yo'q", reply_markup=cancelKeyboards)


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


# Reject

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

    reason = f"""Afsuski sizning premium obunaga bo'lgan so'rovingiz bekor qilindi.
Sababi: {message.text}
Biror xatolik ketgan bo'lsa bizga murojat qiling: @texnosupportuzbot
"""
    try:
        await bot.send_message(chatId, reason)
    except BotBlocked:
        print("Bot blocked!")

    SubscriptionManager.rejectPremiumRequest(chatId)
    
    await state.finish()
    return await message.answer("Premium obuna rad etildi", reply_markup=adminKeyboards)




# without_inline


# Callback with and without inline


@dp.callback_query_handler(text="without_inline")
async def checkIsSubscripted(message: types.Message):
    await AdminSendMessage.type_.set()
    await bot.send_message(message.from_user.id, "Kimlarga yuborishni tanlang, FREE/ALL")
    return await message.answer("Kimlarga yuborishni tanlang, FREE/ALL")



@dp.message_handler(state=AdminSendMessage.type_)
async def setType(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data["type_"] = message.text


    await bot.send_message(message.from_user.id, "Xabar/Rasm/Video kiriting")
    await AdminSendMessage.next()



# Send without inline


@dp.message_handler(state=AdminSendMessage.message, content_types=types.ContentType.ANY)
async def sendToUsersMessage(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        type_ = data["type_"]

    sendAny = SendAny(message)


    if type_ == "FREE":
        users = PlanManager.getFreePlanUsers()
    elif type_ == "ALL":
        users = ChatManager.all()
    else:
        await state.finish()
        return await message.answer("Bekor qilindi!", reply_markup=adminKeyboards)

    blockedUsersCount = 0
    
    for user in users:
        try: 

            if message.content_type == "text":
                resp = await sendAny.sendMessage(user.chatId, blockedUsersCount)
                blockedUsersCount = blockedUsersCount + resp
            elif message.content_type == "photo":
                resp = await sendAny.sendPhoto(user.chatId, blockedUsersCount)
                blockedUsersCount = blockedUsersCount + resp
            elif message.content_type == "video":
                resp = await sendAny.sendVideo(user.chatId, blockedUsersCount)
                blockedUsersCount = blockedUsersCount + resp
            elif message.content_type == "animation":
                resp = await sendAny.sendAnimation(user.chatId, blockedUsersCount)
                blockedUsersCount = blockedUsersCount + resp
            
        except BaseException as e:
            print(e)
    
    await sendError(f"Bot was blocked by {blockedUsersCount} users")

    await state.finish()
    return await message.answer("Xabar yuborildi!")


# Callbact with inline 
@dp.callback_query_handler(text="with_inline")
async def checkIsSubscripted(message: types.Message):
    await SendMessageWithInlineState.buttons.set()

    await bot.send_message(message.from_user.id,"Inline buttonlarni kiriting. Misol uchun\n`./Test-t.me//texnomasters\n./Test2-t.me//texnomasters`", parse_mode='MARKDOWN')
    return await message.answer("Inline")


# With inline  buttons set  

@dp.message_handler(state=SendMessageWithInlineState.buttons)
async def setButtons(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["buttons"] = message.text
    
    await SendMessageWithInlineState.next()
    return await message.answer("Xabar/Rasm/Video kiriting")



# Send with inline
@dp.message_handler(state=SendMessageWithInlineState.message, content_types=types.ContentType.ANY)
async def sendMessageWithInline(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        inline_keyboards_text = data["buttons"]
        
        inline_keyboards = extract_inline_buttons(inline_keyboards_text)
        inline_keyboards = dynamic_sendMenu(inline_keyboards)

        sendAny = SendAny(message)

        users = PlanManager.getFreePlanUsers()

        blockedUsersCount = 0

        for user in users:
            try: 
                if message.content_type == "text":
                    await sendAny.sendMessage(user.chatId, blockedUsersCount, inline_keyboards)
                elif message.content_type == "photo":
                    await sendAny.sendPhoto(user.chatId, blockedUsersCount, inline_keyboards)
                elif message.content_type == "video":
                    await sendAny.sendVideo(user.chatId, blockedUsersCount, inline_keyboards)
                elif message.content_type == "animation":
                    await sendAny.sendAnimation(user.chatId, blockedUsersCount, inline_keyboards)
                
            except BaseException as e:
                print(e)    
    

    await sendError(f"Bot was blocked by {blockedUsersCount} users")
    
    await state.finish()

    return await message.answer("Xabar yuborildi!")





