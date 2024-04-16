from aiogram.fsm.state import StatesGroup, State


class AdminLoginState(StatesGroup):
    password = State()


class AdminSendMessage(StatesGroup):
    userType = State()
    message = State()


class SendMessageWithInlineState(StatesGroup):
    buttons = State()
    message = State()


class PaymentState(StatesGroup):
    awaitingPaymentConfirmation = State()
    awaitingPhotoProof = State()


class ConfirmSubscriptionState(StatesGroup):
    receiverId = State()


class RejectState(StatesGroup):
    receiverId = State()
    reason = State()


class FeedbackMessageState(StatesGroup):
    text = State()
