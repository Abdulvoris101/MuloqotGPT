from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils import constants


bot = Bot(token=constants.BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

