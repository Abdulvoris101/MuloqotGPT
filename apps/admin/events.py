from bot import bot
from apps.common.settings import settings


async def sendEvent(text: str):
    await bot.send_message(settings.EVENT_CHANNEL_ID, text, parse_mode='HTML')


async def sendError(text: str):
    await bot.send_message(settings.ERROR_CHANNEL_ID, text, parse_mode='HTML')
