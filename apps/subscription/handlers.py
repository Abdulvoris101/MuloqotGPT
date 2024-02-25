from aiogram.dispatcher.dispatcher import FSMContext
from bot import dp, bot, types
from utils import text, constants
from utils.events import sendSubscriptionEvent
from db.state import PaymentState
from .keyboards import checkPaymentMenu, cancelMenu, buySubscriptionMenu
from aiogram.dispatcher.filters import Text
from apps.subscription.managers import SubscriptionManager, PlanManager


@dp.callback_query_handler(text="subscribe_premium")
async def buyPremium(message: types.Message):
    user = message.from_user
    premiumPlan = PlanManager.getPremiumPlanOrCreate()

    notPaidSubscription = SubscriptionManager.getNotPaidPremiumSubscription(
        user.id, premiumPlan.id)
    payedSubscription = SubscriptionManager.getPremiumSubscription(
        user.id, premiumPlan.id)
    
    if notPaidSubscription is not None:
        await message.answer("Sizning premium obunaga so'rovingiz ko'rib chiqilmoqda")
        return
    if payedSubscription is not None:
        await message.answer("Siz allaqachon premium obunaga egasiz")
        return
    
    await message.answer("Sotib olish")
    await bot.send_message(
        message.from_user.id,
        text.subscriptionInvoiceText(int(constants.PREMIUM_PRICE)),
        reply_markup=checkPaymentMenu)

    await PaymentState.first_step.set()


@dp.message_handler(commands=["premium"])
async def premium(message: types.Message):
    if message.chat.type == "private":
        await bot.send_message(
            message.chat.id, 
            text.PLAN_DESCRIPTION_TEXT,
            reply_markup=buySubscriptionMenu
        )


@dp.message_handler(Text(equals="Skrinshotni yuborish"), state=PaymentState.first_step)
async def topUpBalance(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["price"] = constants.PREMIUM_PRICE
        
    sentMessage = await message.answer("Biroz kuting...")

    await bot.delete_message(message.chat.id, sentMessage.message_id)
    await message.answer(text.PAYMENT_STEP_1, reply_markup=cancelMenu)

    await PaymentState.next()


@dp.message_handler(state=PaymentState.second_step, content_types=types.ContentTypes.PHOTO)
async def subscriptionCreate(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        price = data["price"]
        
    photoFileId = message.photo[-1].file_id

    SubscriptionManager.unsubscribe(
        planId=PlanManager.getFreePlanOrCreate().id,
        chatId=message.from_user.id
    )

    subscription = SubscriptionManager.createSubscription(
        planId=PlanManager.getPremiumPlanOrCreate().id,
        chatId=message.from_user.id,
        cardholder=None,
        is_paid=False,
        isFree=False
    )

    await sendSubscriptionEvent(f"""#payment check-in\nchatId: {message.from_user.id},\nsubscription_id: {subscription.id},\nfile id: {photoFileId},\nprice: {price}""")

    await bot.send_photo(constants.SUBSCRIPTION_CHANNEL_ID, photoFileId)
    await message.answer(text.PAYMENT_STEP_2, reply_markup=types.ReplyKeyboardRemove())
    
    await state.finish()


@dp.message_handler(commands=["donate"])
async def donate(message: types.Message):
    return await message.reply(text.DONATE)
