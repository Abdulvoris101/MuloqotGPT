from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminLoginState(StatesGroup):
    password = State()

class AdminSystemMessageState(StatesGroup):
    message = State()

class AdminUserAddState(StatesGroup):
    telegramId = State()
    username = State()
    name = State()


class PerformIdState(StatesGroup):
    performid = State()

class AdminSendMessage(StatesGroup):
    message = State()

class SendMessageWithInlineState(StatesGroup):
    buttons = State()
    message = State()



class PaymentState(StatesGroup):
    first_step = State()
    second_step = State()
    
class TopupState(StatesGroup):
    chat_id = State()
    sure = State()


class RejectState(StatesGroup):
    chat_id = State()
    reason = State()
    