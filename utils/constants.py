from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get("API_KEY")
FREE_API_KEY = os.environ.get("FREE_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PASSWORD= os.environ.get("PASSWORD")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ERROR_CHANNEL_ID= os.environ.get("ERROR_CHANNEL_ID")
EVENT_CHANNEL_ID= os.environ.get("EVENT_CHANNEL_ID")
PHONE = os.environ.get("PHONE")
PASSWORD_PAYME = os.environ.get("PASSWORD_PAYME")
DEVICE = os.environ.get("DEVICE")
AQSHA_COST= os.environ.get("AQSHA_COST")
WEB_URL= os.environ.get("WEB_URL")

DB_URL=os.environ.get("DB_URL")


