from aiogram import Router, F, types
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from bot import bot
from utils import text, constants
from utils.events import sendSubscriptionEvent
from db.state import PaymentState
from .keyboards import checkPaymentMenu, cancelMenu, buySubscriptionMenu
from apps.subscription.managers import SubscriptionManager, PlanManager


subscriptionRouter = Router(name="subscriptionRouter")


@subscriptionRouter.message(Command("premium"))
async def premium(message: types.Message):
    if message.chat.type == "private":
        await bot.send_message(
            message.chat.id, 
            text.PLAN_DESCRIPTION_TEXT,
            reply_markup=buySubscriptionMenu
        )


@subscriptionRouter.callback_query(F.data == "subscribe_premium")
async def buyPremium(message: types.Message, state: FSMContext):
    user = message.from_user
    premiumPlanId = PlanManager.getPremiumPlanId()

    notPaidSubscription = SubscriptionManager.getUnpaidPremiumSubscription(
        user.id, premiumPlanId)
    payedSubscription = SubscriptionManager.getPremiumSubscription(
        user.id, premiumPlanId)

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

    await state.set_state(PaymentState.first_step)


@subscriptionRouter.message(F.text == "Skrinshotni yuborish", PaymentState.first_step)
async def checkThePayment(message: types.Message, state: FSMContext):
    sentMessage = await message.answer("Biroz kuting...")

    await state.update_data(price=constants.PREMIUM_PRICE)
    await bot.delete_message(message.chat.id, sentMessage.message_id)
    await message.answer(text.PAYMENT_STEP_1, reply_markup=cancelMenu)

    await state.set_state(PaymentState.second_step)


@subscriptionRouter.message(PaymentState.second_step, F.photo)
async def createSubscription(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = data.get("price")

    photoFileId = message.photo[-1].file_id

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
    
    await state.clear()


@subscriptionRouter.message(Command("donate"))
async def donate(message: types.Message):
    return await message.reply(text.DONATE)
