from aiogram.dispatcher import FSMContext
import os
from app import dp, types, AdminLoginState, AdminSystemMessageState, AdminSendMessage, bot
from db.manager import  Admin, Message, Group
from aiogram.utils.exceptions import BotKicked

@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state=None):
    
    await AdminLoginState.password.set()

    await message.answer(""" Password kiriting!""")


@dp.message_handler(commands=['add_rule'])
async def add_rule_command(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        await AdminSystemMessageState.message.set()

        return await message.answer(""" Qoidani faqat ingliz yoki rus tilida kiriting!""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun""")



@dp.message_handler(commands=['send_message'])
async def send_message_command(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        await AdminSendMessage.message.set()
        return await message.answer(""" Xabarni kiriting iloji boricha rus va o'zbek tilida!""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun """)




@dp.message_handler(state=AdminSendMessage.message)
async def send_message(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data['message'] = message.text

    chats = Group().get_chats()

    for chat in chats:
        try:
            await bot.send_message(chat_id=chat[3], text=message.text)
        except BotKicked as e:
            print(chat[3])
            print("Error", e)

    await state.finish()

    return await message.answer(""" Xabar  yuborildi !""")


@dp.message_handler(state=AdminSystemMessageState.message)
async def add_rule(message: types.Message, state=FSMContext):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    async with state.proxy() as data:
        data['message'] = message.text

    if is_admin:
        await state.finish()
        Admin().add_rule(message=message.text)
        return await message.answer(""" Rule kiritilndi!""")

    return await message.answer("""Afsuski bu so'rov faqat admin uchun""")



@dp.message_handler(state=AdminLoginState.password)
async def password_handler(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data['password'] = message.text

    if message.text == str(os.environ.get('PASSWORD')):
        admin = Admin()
        
        await state.finish()    
        
        admin.register_admin(message.from_user.id)

        await message.answer("Qaytganiz bilan Admin!")

        return ""

    return await message.answer("""Notog'ri parol!""")



@dp.message_handler(commands=['errors'])
async def geterrors_handler(message: types.Message):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        return await message.answer(Admin().get_errors())
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")



@dp.message_handler(commands=['users'])
async def getusers_handler(message: types.Message):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        return await message.answer(Admin().get_users())
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")


