from aiogram.dispatcher import FSMContext
import os
from app import dp, types, AdminLoginState, AdminSystemMessageState, AdminAdsMessage, AdminUserAddState,  AdminSendMessage, bot, PerformIdState
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


@dp.message_handler(Text(equals=".📊 Statistika"))
async def get_statistics(message: types.Message):
    if Admin.is_admin(user_id=message.from_user.id):
        return await message.answer(f"👤 Foydalanuvchilar - {Chat.users()}.\n👥 Guruhlar - {Chat.groups()}\n📥Xabarlar - {Message.count()}")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")


@dp.message_handler(Text(equals=".📤 Xabar yuborish"))
async def send_message_command(message: types.Message, state=None):
    if Admin.is_admin(user_id=message.from_user.id):

        await AdminSendMessage.message.set()
        return await message.answer("Xabarni kiriting")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")


@dp.message_handler(state=AdminSendMessage.message)
async def send_message(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data['message'] = message.text

    if Admin.is_admin(user_id=message.from_user.id):

        await state.finish()

        if len(message.text) > 4000:
            return await message.answer("Juda katta matn!")

        chats = Chat.all()

        for chat in chats:
            try: 
                sent_message = await bot.send_message(chat_id=chat[3], text=message.text)
                AdminMessage(message=str(sent_message.text), message_id=int(sent_message.message_id), chat_id=chat[3]).save()
            
            except BaseException as e:
                print(e)
                print(chat[3])

        return await message.answer("Xabar yuborildi!")

    return await message.answer("Afsuski bu so'rov faqat admin uchun!")



@dp.message_handler(Text(equals=".🌄 Reklama yuborish"))
async def send_ads_command(message: types.Message, state=None):

    if Admin.is_admin(user_id=message.from_user.id):

        await AdminAdsMessage.message_photo.set()
        
        return await message.answer("Reklama postni yuboring!")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=AdminAdsMessage.message_photo)
async def send_adsmessage(message: types.Message, state=FSMContext):

    if Admin.is_admin(user_id=message.from_user.id):
        

        async with state.proxy() as data:
            data['message_photo'] = message.photo[-1].file_id


        chats = Chat.all()

        for chat in chats:
            try: 
                await bot.send_photo(chat_id=chat[3], photo=message.photo[-1].file_id, caption=message.caption)
            except BaseException as e:
                pass
    
        await state.finish()

        return await message.answer("Xabar yuborildi!")

    return await message.answer("Afsuski bu so'rov faqat admin uchun!")



@dp.message_handler(Text(equals=".‼️ Xatoliklar"))
async def get_errors_handler(message: types.Message):
    is_admin = Admin.is_admin(user_id=message.from_user.id)

    if not is_admin:
        return await message.answer("Afsuski bu so'rov faqat admin uchun")

    await message.answer(Error.all())





# @dp.message_handler(Text(equals=".👥 Foydalanuvchi qo'shish"))
# async def add_user_command(message: types.Message, state=None):
#     if Admin.is_admin(user_id=message.from_user.id):
        
#         await AdminUserAddState.telegramId.set()

#         return await message.answer("Telegram Id kiriting")
    
#     return await message.answer("Afsuski bu so'rov faqat admin uchun")



# @dp.message_handler(state=AdminUserAddState.telegramId)
# async def telegramId_set(message: types.Message, state:FSMContext):
#     if Admin.is_admin(user_id=message.from_user.id):

#         async with state.proxy() as data:
#             data["telegramId"] = message.text
                
#         await AdminUserAddState.next()

#         return await message.answer("UserName kiriting")
    
#     return await message.answer("Afsuski bu so'rov faqat admin uchun")


# @dp.message_handler(state=AdminUserAddState.username)
# async def name_set(message: types.Message, state:FSMContext):
#     if Admin.is_admin(user_id=message.from_user.id):


#         async with state.proxy() as data:
#             data["username"] = message.text
        
#         await AdminUserAddState.next()

#         return await message.answer("Name kiriting")
    
#     return await message.answer("Afsuski bu so'rov faqat admin uchun")


# @dp.message_handler(state=AdminUserAddState.name)
# async def username_set(message: types.Message, state:FSMContext):
#     if Admin.is_admin(user_id=message.from_user.id):


#         async with state.proxy() as data:
#             data["name"] = message.text

#             chat = Chat(chat_id=data["telegramId"], chat_name=data["name"], username=data["username"])

#             chat.save()

#         await AdminUserAddState.next()

#         await state.finish()

#         return await message.answer("Foydalanuvchi kiritilindi!")

    
#     return await message.answer("Afsuski bu so'rov faqat admin uchun")
