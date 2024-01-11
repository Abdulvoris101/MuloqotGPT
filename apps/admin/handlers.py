from aiogram.dispatcher import FSMContext
import os
from bot import dp, types, bot
from db.state import AdminLoginState, AdminSystemMessageState, PopupState, SendMessageWithInlineState,  AdminSendMessage, PerformIdState
from .models import Admin
from apps.core.managers import ChatManager, MessageManager
from .keyboards import admin_keyboards, cancel_keyboards, sendMessageMenu, dynamic_sendMenu
from aiogram.dispatcher.filters import Text
from utils import SendAny, extract_inline_buttons, constants
from filters import IsAdmin
import math


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
    return await message.answer(f"👤 Foydalanuvchilar - {ChatManager.users()}.\n💥 Aktiv Foydalanuvchilar - {ChatManager.active_users()}\n👥 Guruhlar - {ChatManager.groups()}\n📥Xabarlar - {MessageManager.count()}")
    

@dp.message_handler(IsAdmin(), Text(equals="📤 Xabar yuborish.!"))
async def send_message_command(message: types.Message, state=None):
    return await message.answer("Xabarni turini kiriting", reply_markup=sendMessageMenu)

# without_inline


# Callback with and without inline


@dp.callback_query_handler(text="without_inline")
async def check_issubscripted(message: types.Message):
    await AdminSendMessage.message.set()
    await bot.send_message(message.from_user.id,"Xabar/Rasm/Video kiriting")
    return await message.answer("Xabar/Rasm/Video kiriting")

# Send without inline


@dp.message_handler(state=AdminSendMessage.message, content_types=types.ContentType.ANY)
async def send_message(message: types.Message, state=FSMContext):

    await state.finish()

    sendAny = SendAny(message)

    chats = ChatManager.all()

    for chat in chats:
        try: 
            if message.content_type == "text":
                await sendAny.send_message(chat.chat_id)
            elif message.content_type == "photo":
                await sendAny.send_photo(chat.chat_id)
            elif message.content_type == "video":
                await sendAny.send_video(chat.chat_id)
            
        except BaseException as e:
            print(e)

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

        chats = ChatManager.all()

        for chat in chats:
            try: 
                if message.content_type == "text":
                    await sendAny.send_message(chat.chat_id, inline_keyboards)
                elif message.content_type == "photo":
                    await sendAny.send_photo(chat.chat_id, inline_keyboards)
                elif message.content_type == "video":
                    await sendAny.send_video(chat.chat_id, inline_keyboards)
                
            except BaseException as e:
                print(e)
                print(chat.chat_id)
    
    
    await state.finish()

    return await message.answer("Xabar yuborildi!")





