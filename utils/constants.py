from dotenv import load_dotenv
import os
from aiogram import types

load_dotenv()

API_KEY = os.environ.get("API_KEY")
FREE_API_KEY = os.environ.get("FREE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PASSWORD = os.environ.get("PASSWORD")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ERROR_CHANNEL_ID = os.environ.get("ERROR_CHANNEL_ID")
EVENT_CHANNEL_ID = os.environ.get("EVENT_CHANNEL_ID")
SUBSCRIPTION_CHANNEL_ID = os.environ.get("SUBSCRIPTION_CHANNEL_ID")
PHONE = os.environ.get("PHONE")
PASSWORD_PAYME = os.environ.get("PASSWORD_PAYME")
DEVICE = os.environ.get("DEVICE")
AQSHA_COST = os.environ.get("AQSHA_COST")
WEB_URL = os.environ.get("WEB_URL")
DB_URL = os.environ.get("DB_URL")
REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
HOST_GROUP_ID = int(os.environ.get("HOST_GROUP_ID"))
IMAGE_GEN_GROUP_ID = int(os.environ.get("IMAGE_GEN_GROUP_ID"))
COMMENTS_GROUP_ID = int(os.environ.get("COMMENTS_GROUP_ID"))
ALLOWED_GROUPS = [HOST_GROUP_ID, IMAGE_GEN_GROUP_ID]
AVAILABLE_GROUP_TYPES = [types.ChatType.GROUP, types.ChatType.SUPERGROUP]

IMAGE_GENERATION_WORDS = ["generate", "imagine"]

# PRICE

FREE_GPT_REQUESTS_MONTHLY = 480
FREE_IMAGEAI_REQUESTS_MONTHLY = 150

GROUP_HOST_GPT_REQUESTS_MONTHLY = 4500
GROUP_HOST_IMAGEAI_REQUESTS_MONTHLY = 3000

PREMIUM_GPT_REQUESTS_MONTHLY = 2250
PREMIUM_IMAGEAI_REQUESTS_MONTHLY = 900

PREMIUM_PRICE = 25000
HOST_GROUP_PRICE = 36000
