from aiogram.dispatcher import FSMContext
import os
from app import dp, types, AdminLoginState, AdminSystemMessageState, AdminSendMessage, bot, PerformIdState
from db.manager import  Admin, Message, Group
from aiogram.utils.exceptions import BotKicked
import uuid

admin_text = """"Xush kelibsiz Admin!
/users - chatlar
/errors - xatoliklar
/sent_messages - admin tomonidan yuborilgan xabarlar!
/send_message - xabar yuborish.
/delete_message - perform id bo'yicha o'chirish.
/add_rule - system xabar qo'shish.
/statistics - statistika."""


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state=None):
    
    if Admin().is_admin(message.from_user.id):
        await message.answer(admin_text)
        return ""
 
    
    await AdminLoginState.password.set()

    return await message.answer(""" Password kiriting!""")




@dp.message_handler(state=AdminLoginState.password)
async def password_handler(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data['password'] = message.text

    if message.text == str(os.environ.get('PASSWORD')):
        admin = Admin()
        
        await state.finish()    
        
        admin.register_admin(message.from_user.id)

        await message.answer(admin_text)

        return ""

    return await message.answer("""Notog'ri parol!""")




@dp.message_handler(commands=['add_rule'])
async def add_rule_command(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        await AdminSystemMessageState.message.set()

        return await message.answer(""" Qoidani faqat ingliz yoki rus tilida kiriting!""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun""")



@dp.message_handler(commands=['statistics'])
async def get_statistics(message: types.Message):
    
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        return await message.answer(f"👥 Users - {Admin().get_users_count()}.\n📥Messages - {Admin().get_messages_count()}")
    
    return await message.answer("Afsuski bu so'rov faqat admin uchun")



@dp.message_handler(commands=['send_message'])
async def send_message_command(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        await AdminSendMessage.message.set()
        return await message.answer(""" Xabarni kiriting iloji boricha rus va o'zbek tilida!""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun """)



@dp.message_handler(commands=['sent_messages'])
async def send_message_command(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        messages = Admin().get_sent_messages()

        return await message.answer(messages)
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun """)



@dp.message_handler(commands=['delete_message'])
async def delete_messages(message: types.Message, state=None):
    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:
        await PerformIdState.performid.set()
        return await message.answer(""" Perform Id kiriting""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun """)



@dp.message_handler(state=PerformIdState.performid)
async def delete_messages_do(message: types.Message, state=FSMContext):
    is_admin = Admin().is_admin(user_id=message.from_user.id)
    delete_messageids = Admin().get_deleting_messageids(perform_id=message.text)

    if is_admin:
        await state.finish()

        for message_obj in delete_messageids:
            try:
                await bot.delete_message(chat_id=int(message_obj[4]), message_id=int(message_obj[3]))
            except:
                pass

        Admin().delete_messages_by_perform(perform_id=message.text)

        return await message.answer(""" Xabar o'chirildi!""")
    
    return await message.answer(""" Afsuski bu so'rov faqat admin uchun """)





@dp.message_handler(state=AdminSendMessage.message)
async def send_message(message: types.Message, state=FSMContext):

    async with state.proxy() as data:
        data['message'] = message.text

    is_admin = Admin().is_admin(user_id=message.from_user.id)

    if is_admin:

        chats = Group().get_chats()

        await state.finish()
        random_str = str(uuid.uuid4())

        for chat in chats:
            try: 
                sent_message = await bot.send_message(chat_id=chat[3], text=message.text)
                Admin().add_admin_message(str(sent_message.text), perform_id=random_str, message_id=int(sent_message.message_id), chat_id=chat[3])
           
            except BaseException as e:
                print(e)
                print(chat[3])

        return await message.answer(""" Xabar  yuborildi !""")

    return await message.answer(""" Afsuski bu so'rov faqat admin uchun !""")
    


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


