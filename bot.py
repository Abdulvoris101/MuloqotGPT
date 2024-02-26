from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from utils import constants


bot = Bot(token=constants.BOT_TOKEN, parse_mode='HTML')
storage = RedisStorage2(constants.REDIS_HOST, 6379, db=1, pool_size=10)


dp = Dispatcher(bot, storage=storage)
