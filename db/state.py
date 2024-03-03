from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminLoginState(StatesGroup):
    password = State()


class AdminSystemMessageState(StatesGroup):
    message = State()


class AdminSendMessage(StatesGroup):
    userType = State()
    message = State()


class SendMessageWithInlineState(StatesGroup):
    buttons = State()
    message = State()


class PaymentState(StatesGroup):
    first_step = State()
    second_step = State()


class TopupState(StatesGroup):
    chatId = State()
    sure = State()


class RejectState(StatesGroup):
    chatId = State()
    reason = State()


class Comment(StatesGroup):
    message = State()