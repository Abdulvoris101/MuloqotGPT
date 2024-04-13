from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis

from utils import constants

redis = Redis(host=constants.REDIS_HOST, port=6379, db=1)

bot = Bot(token=constants.BOT_TOKEN, parse_mode='HTML')
storage = RedisStorage(redis=redis)


dp = Dispatcher(storage=storage)
