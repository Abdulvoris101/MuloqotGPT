from bot import dp, bot, types
from utils import text, constants
from db.state import PaymentState
from aiogram.dispatcher.dispatcher import FSMContext
import uuid
from .keyboards import check_payment_menu
from aiogram.dispatcher.filters import Text
from utils import send_event
from apps.imageai.keyboards import buyCreditMenu
from apps.subscription.managers import SubscriptionManager, PlanManager



@dp.callback_query_handler(text="subscribe_premium")
async def buy_premium(message: types.Message):

    notPaidSubscription = SubscriptionManager.getNotPaidPremiumSubsctiption(message.from_user.id, PlanManager.getPremiumPlanOrCreate().id)
    payedSubscription = SubscriptionManager.getNotPaidPremiumSubsctiption(message.from_user.id, PlanManager.getPremiumPlanOrCreate().id)
    
    if notPaidSubscription is not None:
        await message.answer("Sizning premium obunaga so'rovingiz ko'rib chiqilmoqda")
        return
    if payedSubscription is not None:
        await message.answer("Siz allaqachon premium obunaga egasiz")
        return
    
    await message.answer("Sotib olish")
    
    await bot.send_message(
        message.from_user.id,
        text.buy_text(int(constants.PREMIUM_PRICE)), 
        reply_markup=check_payment_menu)

    await PaymentState.first_step.set()


@dp.message_handler(commands=["premium"])
async def premium(message: types.Message):
    await bot.send_message(
        message.chat.id, 
        text.PLAN_TEXT,
        reply_markup=buyCreditMenu
    )


@dp.message_handler(Text(equals="Davom etish"), state=PaymentState.first_step)
async def topup_balance(message: types.Message, state=FSMContext):   
     
    async with state.proxy() as data:
        data["price"] = constants.PREMIUM_PRICE
        
    sent_message = await message.answer("Biroz kuting...")

    await bot.delete_message(message.chat.id, sent_message.message_id)

    await message.answer(text.PAYMENT_STEP1, reply_markup=types.ReplyKeyboardRemove())
    
    await PaymentState.next()


@dp.message_handler(state=PaymentState.second_step)
async def subscription_create(message: types.Message, state=FSMContext):

    
    async with state.proxy() as data:
        price = data["price"]
        
    cardholder = message.text

    SubscriptionManager.unsubscribe(
        plan_id=PlanManager.getFreePlanOrCreate().id,
        chat_id=message.from_user.id
    )

    subscription = SubscriptionManager.create_subscription(
        plan_id=PlanManager.getPremiumPlanOrCreate().id,
        chat_id=message.from_user.id,
        cardholder=cardholder,
        is_paid=False,
        is_free=False
    )

    await send_event(f"""#payment check-in\nchatId: {message.from_user.id},\nsubscription_id: {subscription.id},\ncardholder: {cardholder},\nprice: {price}""")

    await message.answer(text.PAYMENT_STEP2)
    
    await state.finish()
