from aiogram.dispatcher import FSMContext
import os
from bot import dp, types, bot
from db.state import AdminLoginState, AdminSystemMessageState, SendMessageWithInlineState,  AdminSendMessage, TopupState, RejectState
from .models import Admin
from apps.core.managers import ChatManager, MessageManager, MessageStatManager
from apps.core.models import MessageStats
from .keyboards import admin_keyboards, cancel_keyboards, sendMessageMenu, dynamic_sendMenu
from aiogram.dispatcher.filters import Text
from utils import SendAny, extract_inline_buttons, constants, text
from filters import IsAdmin
from apps.subscription.managers import SubscriptionManager, PlanManager



@dp.message_handler(commands=["cancel"], state='*')
async def cancel(message: types.Message, state: FSMContext):   
    await state.finish()
    if Admin.is_admin(message.from_user.id):
        return await bot.send_message(message.chat.id, "State bekor qilindi!", reply_markup=admin_keyboards)
    
    return await bot.send_message(message.chat.id, "Bekor qilindi!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state=None):
    if Admin.is_admin(message.from_user.id):
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!", reply_markup=admin_keyboards)
 
    await AdminLoginState.password.set()
    return await message.answer("Password kiriting!")


@dp.message_handler(state=AdminLoginState.password)
async def password_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    if message.text == str(constants.PASSWORD):
        await state.finish()
        Admin(message.from_user.id).register(message.from_user.id)
        
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!", reply_markup=admin_keyboards)
    
    return await message.answer("Noto'g'ri parol!")


@dp.message_handler(IsAdmin(), Text(equals="🤖 System xabar yuborish.!"))
async def add_rule_command(message: types.Message, state=None):        
    await AdminSystemMessageState.message.set()

    return await message.answer("Qoidani faqat ingliz yoki rus tilida kiriting!", reply_markup=cancel_keyboards)
    

@dp.message_handler(IsAdmin(), state=AdminSystemMessageState.message)
async def add_rule(message: types.Message, state=FSMContext):    
    async with state.proxy() as data:
        data['message'] = message.text

    await state.finish()
    
    MessageManager.system_to_allchat(text=message.text)
    return await message.answer("System xabar kiritildi!")



@dp.message_handler(IsAdmin(), Text(equals="📊 Statistika.!"))
async def get_statistics(message: types.Message):
    return await message.answer(f"👤 Foydalanuvchilar - {ChatManager.users()}.\n💥 Aktiv Foydalanuvchilar - {ChatManager.active_users()}\n📥Xabarlar - {MessageManager.count()}")
    

@dp.message_handler(IsAdmin(), Text(equals="📤 Xabar yuborish.!"))
async def send_message_command(message: types.Message, state=None):
    return await message.answer("Xabarni turini kiriting", reply_markup=sendMessageMenu)


# Subscribe

@dp.message_handler(IsAdmin(), Text(equals="🎁 Premium obuna.!"))
async def subscribe_user(message: types.Message):
    await TopupState.chat_id.set()
    return await message.answer("Chat id kiriting", reply_markup=cancel_keyboards)


@dp.message_handler(IsAdmin(), state=TopupState.chat_id)
async def set_chat_id(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        data['chat_id'] = message.text

    premium_subscription = SubscriptionManager.getNotPaidPremiumSubsctiption(
        chat_id=message.text, plan_id=PlanManager.getPremiumPlanOrCreate().id)
    
    if premium_subscription is None:
        await state.finish()
        return await message.answer("Foydalanuvchiga premium obuna taqdim etib bo'lmaydi!")
    
    await TopupState.next()
    return await message.answer("Siz rostan ushbu userga premium obuna taqdim etmoqchimisiz? Xa/Yo'q", reply_markup=cancel_keyboards)


@dp.message_handler(IsAdmin(), state=TopupState.sure)
async def subscribe_user(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        chat_id = data['chat_id']

    if message.text != "Xa":
        await state.finish()
        return await message.answer("Bekor qilindi!", reply_markup=admin_keyboards)
 
    
    SubscriptionManager.unsubscribe(
        PlanManager.getFreePlanOrCreate().id,
        chat_id=chat_id
    )
    
    messageStat = MessageStats.get(chat_id=chat_id)
    MessageStats.update(messageStat, "todays_messages", 20 - messageStat.todays_messages)

    
    SubscriptionManager.subscribe(
        chat_id=chat_id, plan_id=PlanManager.getPremiumPlanOrCreate().id)
    
    await bot.send_message(chat_id, text.PREMIUM_GAVE)
    
    await state.finish()
    return await message.answer("Ushbu foydalanuvchi premium obunaga ega bo'ldi 🎉", reply_markup=admin_keyboards)


# Reject

@dp.message_handler(IsAdmin(), Text(equals="✖️ Premiumni rad etish.!"))
async def cancel_subscription(message: types.Message):
    await RejectState.chat_id.set()
    return await message.answer("Chat id kiriting", reply_markup=cancel_keyboards)


@dp.message_handler(IsAdmin(), state=RejectState.chat_id)
async def set_chat_id_reject(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        data['chat_id'] = message.text

    await RejectState.next()
    return await message.answer("Sababni kiriting", reply_markup=cancel_keyboards)


@dp.message_handler(IsAdmin(), state=RejectState.reason)
async def reject_reason(message: types.Message, state=FSMContext):  

    async with state.proxy() as data:
        chat_id = data['chat_id']

    reason = f"""Afsuski sizning premium obunaga bo'lgan so'rovingiz bekor qilindi.
Sababi: {message.text}
"""
    await bot.send_message(chat_id, reason)
    
    SubscriptionManager.rejectPremiumRequest(chat_id)
    
    await state.finish()
    return await message.answer("Premium obuna rad etildi", reply_markup=admin_keyboards)




# without_inline


# Callback with and without inline


@dp.callback_query_handler(text="without_inline")
async def check_issubscripted(message: types.Message):
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
async def send_message(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        type_ = data["type_"]

    sendAny = SendAny(message)


    if type_ == "FREE":
        users = PlanManager.getFreePlanUsers()
    elif type_ == "ALL":
        users = ChatManager.all()
    else:
        await state.finish()
        return await message.answer("Bekor qilindi!", reply_markup=admin_keyboards)


    for user in users:
        try: 
            if message.content_type == "text":
                await sendAny.send_message(user.chat_id)
            elif message.content_type == "photo":
                await sendAny.send_photo(user.chat_id)
            elif message.content_type == "video":
                await sendAny.send_video(user.chat_id)
            
        except BaseException as e:
            print(e)
    

    await state.finish()
    return await message.answer("Xabar yuborildi!")


# Callbact with inline 
@dp.callback_query_handler(text="with_inline")
async def check_issubscripted(message: types.Message):
    await SendMessageWithInlineState.buttons.set()

    await bot.send_message(message.from_user.id,"Inline buttonlarni kiriting. Misol uchun\n`./Test-t.me//texnomasters\n./Test2-t.me//texnomasters`", parse_mode='MARKDOWN')
    return await message.answer("Inline")


# With inline  buttons set  

@dp.message_handler(state=SendMessageWithInlineState.buttons)
async def set_buttons(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["buttons"] = message.text
    
    await SendMessageWithInlineState.next()
    return await message.answer("Xabar/Rasm/Video kiriting")



# Send with inline
@dp.message_handler(state=SendMessageWithInlineState.message, content_types=types.ContentType.ANY)
async def send_message_with_inline(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        inline_keyboards_text = data["buttons"]
        
        inline_keyboards = extract_inline_buttons(inline_keyboards_text)
        inline_keyboards = dynamic_sendMenu(inline_keyboards)

        sendAny = SendAny(message)

        users = PlanManager.getFreePlanUsers()

        for user in users:
            try: 
                if message.content_type == "text":
                    await sendAny.send_message(user.chat_id, inline_keyboards)
                elif message.content_type == "photo":
                    await sendAny.send_photo(user.chat_id, inline_keyboards)
                elif message.content_type == "video":
                    await sendAny.send_video(user.chat_id, inline_keyboards)
                
            except BaseException as e:
                print(e)
                print(user.chat_id)
    
    
    await state.finish()

    return await message.answer("Xabar yuborildi!")





