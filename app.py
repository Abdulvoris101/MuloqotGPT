from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
# from aiogram..co
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

load_dotenv()  # take environment variables from .env.



bot = Bot(token=os.environ.get('BOT_TOKEN'), parse_mode='HTML')
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)


class AdminLoginState(StatesGroup):
    password = State()

class AdminSystemMessageState(StatesGroup):
    message = State()


class AdminSendMessage(StatesGroup):
    message = State()

if __name__ == '__main__':
    from core.handlers import dp
    from admin.handlers import dp
    from event.handlers import dp
    
    executor.start_polling(dp, skip_updates=True)