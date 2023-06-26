from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
# from aiogram..co
from aiogram.contrib.fsm_storage.memory import MemoryStorage


load_dotenv()  # take environment variables from .env.

bot = Bot(token=os.environ.get('BOT_TOKEN'), parse_mode='HTML')
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
