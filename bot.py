import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from apps.common.settings import settings

redis = Redis(host=settings.REDIS_HOST, port=6379, db=1)

bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
storage = RedisStorage(redis=redis)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log',  # Logs will be stored in 'bot.log'
                    filemode='a')  # 'a' means append (add new log entries to the end of the file)
logger = logging.getLogger(__name__)

dp = Dispatcher(storage=storage)
