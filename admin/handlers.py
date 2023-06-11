from aiogram.dispatcher import FSMContext
import os
from app import dp, types, AdminLoginState, AdminSystemMessageState, AdminSendMessage, bot, PerformIdState
from .models import Admin, Error, AdminMessage
from core.models import Message, Chat
from .utils import admin_keyboards
from aiogram.dispatcher.filters import Text


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

    if message.text == str(os.environ.get('PASSWORD')):
        await state.finish()
        Admin(message.from_user.id).register(message.from_user.id)
        
        return await bot.send_message(message.from_user.id, "Xush kelibsiz admin!", reply_markup=admin_keyboards)
    
    return await message.answer("Noto'g'ri parol!")


@dp.message_handler(Text(equals=".🤖 System xabar yuborish"))
async def add_rule_command(message: types.Message, state=None):
    if Admin.is_admin(user_id=message.from_user.id):
        
        await AdminSystemMessageState.message.set()

        return await message.answer("Qoidani faqat ingliz yoki rus tilida kiriting!")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")


@dp.message_handler(Text(equals=".📊 Statistika"))
async def get_statistics(message: types.Message):
    if Admin.is_admin(user_id=message.from_user.id):
        return await message.answer(f"👥 Foydalanuvchilar - {Chat.count()}.\n📥Xabarlar - {Message.count()}")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")

@dp.message_handler(Text(equals=".📤 Xabar yuborish"))
@dp.message_handler(commands=['send_message'])
async def send_message_command(message: types.Message, state=None):
    if Admin.is_admin(user_id=message.from_user.id):

        if len(message.text) > 4000:
            return await message.answer("Juda katta matn!")

        await AdminSendMessage.message.set()
        return await message.answer("Xabarni kiriting iloji boricha rus va o'zbek tilida!")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")




@dp.message_handler(state=AdminSendMessage.message)
async def send_message(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text

    if Admin.is_admin(user_id=message.from_user.id):
        chats = Chat.all()

        await state.finish()

        for chat in chats:
            try: 
                sent_message = await bot.send_message(chat_id=chat[3], text=message.text)
                AdminMessage(message=str(sent_message.text), message_id=int(sent_message.message_id), chat_id=chat[3]).save()
            
            except BaseException as e:
                print(e)
                print(chat[3])

        return await message.answer("Xabar yuborildi!")

    return await message.answer("Afsuski bu so'rov faqat admin uchun!")


@dp.message_handler(state=AdminSystemMessageState.message)
async def add_rule(message: types.Message, state=FSMContext):
    is_admin = Admin.is_admin(user_id=message.from_user.id)
    
    async with state.proxy() as data:
        data['message'] = message.text

    if is_admin:
        await state.finish()
        Message.system_to_all(text=message.text)
        return await message.answer("System xabar kiritildi!")

    return await message.answer("Afsuski bu so'rov faqat admin uchun")


@dp.message_handler(Text(equals=".‼️ Xatoliklar"))
async def get_errors_handler(message: types.Message):
    is_admin = Admin.is_admin(user_id=message.from_user.id)

    if not is_admin:
        return await message.answer("Afsuski bu so'rov faqat admin uchun")

    await message.answer(Error.all())
