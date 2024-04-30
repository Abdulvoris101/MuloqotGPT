from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot
from utils import text
from apps.common.settings import settings
from db.state import PaymentState
from .keyboards import checkPaymentMenu, cancelMenu, getSubscriptionPlansMarkup, PlanCallback
from apps.subscription.managers import SubscriptionManager, PlanManager

subscriptionRouter = Router(name="subscriptionRouter")


@subscriptionRouter.message(Command("premium"), F.chat.type == "private")
async def premium(message: types.Message):
    premiumPlans = PlanManager.filterPlans(isGroup=False, isFree=False)

    await bot.send_message(message.chat.id, text.getSubscriptionPlansText(premiumPlans),
                           reply_markup=getSubscriptionPlansMarkup(premiumPlans))


@subscriptionRouter.callback_query(PlanCallback.filter(F.name == "subscribe_premium"))
async def buyPremium(message: types.Message, user: types.User, callback_data: PlanCallback,
                     state: FSMContext):

    plan = PlanManager.get(callback_data.planId)
    price = "{:,.0f}".format(plan.amountForMonth).replace(",", ".")

    notPaidSubscription = SubscriptionManager.getInActiveSubscription(user.id, callback_data.planId)
    payedSubscription = SubscriptionManager.getActiveSubscription(user.id, callback_data.planId)

    if notPaidSubscription is not None:
        await message.answer(text.PAYMENT_ON_REVIEW_TEXT)
        return
    if payedSubscription is not None:
        await message.answer(text.ALREADY_SUBSCRIBED)
        return

    await bot.send_message(message.from_user.id, text.INVOICE_TEXT.format(price=price),
                           reply_markup=checkPaymentMenu)
    await state.update_data(planId=str(callback_data.planId))
    await state.update_data(price=price)
    await state.set_state(PaymentState.awaitingPaymentConfirmation)


@subscriptionRouter.message(F.text == "Skrinshotni yuborish", PaymentState.awaitingPaymentConfirmation)
async def processPaymentConfirmation(message: types.Message, user: types.User, state: FSMContext):
    sentMessage = await message.answer("Biroz kuting...")

    await bot.delete_message(user.id, sentMessage.message_id)
    await message.answer(text.WAITING_PAYMENT_PHOTO_TEXT, reply_markup=cancelMenu)

    await state.set_state(PaymentState.awaitingPhotoProof)


@subscriptionRouter.message(PaymentState.awaitingPhotoProof, F.photo)
async def handlePaymentSubmission(message: types.Message, user: types.User, state: FSMContext):
    data = await state.get_data()
    photoFileId = message.photo[-1].file_id
    plan = PlanManager.get(planId=data.get("planId"))

    SubscriptionManager.createSubscription(chatId=user.id, is_paid=False,
                                           planId=data.get("planId"))

    subscriptionSendText = text.SUBSCRIPTION_SEND_EVENT_TEXT.format(price=data.get("price"),
                                                                    planId=plan.id, userId=user.id,
                                                                    planTitle=plan.title)
    await bot.send_message(settings.SUBSCRIPTION_CHANNEL_ID, subscriptionSendText, parse_mode='HTML')
    await bot.send_photo(settings.SUBSCRIPTION_CHANNEL_ID, photoFileId)
    await message.answer(text.COMPLETED_PAYMENT, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@subscriptionRouter.message(Command("donate"))
async def donate(message: types.Message):
    return await message.reply(text.DONATE)
