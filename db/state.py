from aiogram.fsm.state import StatesGroup, State


class AdminLoginState(StatesGroup):
    password = State()


class SendMessageToUser(StatesGroup):
    text = State()
    chatId = State()

class SendMessageToUsers(StatesGroup):
    messageType = State()
    userType = State()
    buttons = State()
    message = State()


class PaymentState(StatesGroup):
    planId = State()
    awaitingPaymentConfirmation = State()
    awaitingPhotoProof = State()


class ConfirmSubscriptionState(StatesGroup):
    receiverId = State()
    planId = State()


class RejectState(StatesGroup):
    receiverId = State()
    reason = State()


class ChooseGptModelState(StatesGroup):
    model = State()


class FeedbackMessageState(StatesGroup):
    text = State()

