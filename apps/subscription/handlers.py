from bot import dp, bot, types
from utils import text, constants
from db.state import Payment
from aiogram.dispatcher.dispatcher import FSMContext
from apps.admin.keyboards import cancel_keyboards
import uuid
from .keyboards import check_payment_menu
from aiogram.dispatcher.filters import Text
from .models import Transaction
from utils import send_event
from apps.imageai.keyboards import buyCreditMenu
from apps.subscription.managers import SubscriptionManager, PlanManager



@dp.callback_query_handler(text="subscribe_premium")
async def buy_premium(message: types.Message):
    await message.answer("Sotib olish")
    
    await bot.send_message(
        message.from_user.id,
        text.buy_text(int(constants.PREMIUM_PRICE)), 
        reply_markup=check_payment_menu)

    await Payment.is_success.set()


@dp.message_handler(commands=["premium"])
async def premium(message: types.Message):
    await bot.send_message(
        message.chat.id, 
        text.PLAN_TEXT,
        reply_markup=buyCreditMenu
    )


@dp.message_handler(Text(equals="Davom etish"), state=Payment.is_success)
async def check_payment(message: types.Message, state=FSMContext):   
     
    async with state.proxy() as data:
        data["price"] = constants.PREMIUM_PRICE
        
    sent_message = await message.answer("Biroz kuting...")

    await bot.delete_message(message.chat.id, sent_message.message_id)

    await message.answer(text.PAYMENT_STEP1, reply_markup=types.ReplyKeyboardRemove())
    
    await Payment.next()


@dp.message_handler(state=Payment.full_name)
async def get_full_name_payment(message: types.Message, state=FSMContext):

    subscription_id = uuid.uuid4()
    
    async with state.proxy() as data:
        price = data["price"]
        
    cardholder = message.text


    await send_event(f"""#payment check-in\nchatId: {message.from_user.id},\nsubscription_id: {subscription_id},\ncardholder: {cardholder},\nprice: {price},\nsuccess: Inprogress""")
    
    SubscriptionManager.subscribe(
        plan_id=PlanManager.getPremiumPlanOrCreate(),
        chat_id=message.from_user.id,
        cardholder=cardholder
    )
    
    await message.answer(text.PAYMENT_STEP2)
    
    
    await state.finish()
