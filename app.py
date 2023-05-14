from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
import sqlite3
# from db.manager import 

load_dotenv()  # take environment variables from .env.

bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher(bot)

if __name__ == '__main__':
    from core.handlers import dp
    
    executor.start_polling(dp)