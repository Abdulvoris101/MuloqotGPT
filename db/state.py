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

class AdminAdsMessage(StatesGroup):
    message_photo = State()
