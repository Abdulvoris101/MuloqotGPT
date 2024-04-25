from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot import bot
from utils import text
from apps.common.settings import settings
from db.state import PaymentState
from .keyboards import checkPaymentMenu, cancelMenu, buySubscriptionMenu
from apps.subscription.managers import SubscriptionManager, PlanManager


subscriptionRouter = Router(name="subscriptionRouter")


@subscriptionRouter.message(Command("premium"))
async def premium(message: types.Message):
    if message.chat.type == "private":
        await bot.send_message(message.chat.id, text.CURRENT_PLAN_TEXT,
                               reply_markup=buySubscriptionMenu)


@subscriptionRouter.callback_query(F.data == "subscribe_premium")
async def buyPremium(message: types.Message, user: types.User, state: FSMContext):
    premiumPlanId = PlanManager.getPremiumPlanId()

    notPaidSubscription = SubscriptionManager.getInActiveSubscription(user.id, premiumPlanId)
    payedSubscription = SubscriptionManager.getActiveSubscription(user.id, premiumPlanId)

    if notPaidSubscription is not None:
        await message.answer(text.PAYMENT_ON_REVIEW_TEXT)
        return
    if payedSubscription is not None:
        await message.answer(text.ALREADY_SUBSCRIBED)
        return

    await bot.send_message(message.from_user.id, text.INVOICE_TEXT.format(price=settings.PREMIUM_PRICE),
                           reply_markup=checkPaymentMenu)
    await state.set_state(PaymentState.awaitingPaymentConfirmation)


@subscriptionRouter.message(F.text == "Skrinshotni yuborish", PaymentState.awaitingPaymentConfirmation)
async def processPaymentConfirmation(message: types.Message, user: types.User, state: FSMContext):
    sentMessage = await message.answer("Biroz kuting...")

    await state.update_data(price=settings.PREMIUM_PRICE)
    await bot.delete_message(user.id, sentMessage.message_id)
    await message.answer(text.WAITING_PAYMENT_PHOTO_TEXT, reply_markup=cancelMenu)

    await state.set_state(PaymentState.awaitingPhotoProof)


@subscriptionRouter.message(PaymentState.awaitingPhotoProof, F.photo)
async def handlePaymentSubmission(message: types.Message, user: types.User, state: FSMContext):
    data = await state.get_data()
    photoFileId = message.photo[-1].file_id

    subscription = SubscriptionManager.createSubscription(chatId=user.id, is_paid=False, isFree=False,
                                                          planId=PlanManager.getPremiumPlan().id)

    subscriptionEndText = text.SUBSCRIPTION_SEND_EVENT_TEXT.format(price=data.get("price"),
                                                                   subscriptionId=subscription.id,
                                                                   userId=user.id)
    await bot.send_message(settings.SUBSCRIPTION_CHANNEL_ID, subscriptionEndText, parse_mode='HTML')
    await bot.send_photo(settings.SUBSCRIPTION_CHANNEL_ID, photoFileId)
    await message.answer(text.COMPLETED_PAYMENT, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@subscriptionRouter.message(Command("donate"))
async def donate(message: types.Message):
    return await message.reply(text.DONATE)
