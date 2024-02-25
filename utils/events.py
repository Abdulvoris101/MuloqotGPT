from bot import bot
from . import constants


async def sendEvent(text):
    await bot.send_message(constants.EVENT_CHANNEL_ID, text, parse_mode='HTML')


async def sendSubscriptionEvent(text):
    await bot.send_message(constants.SUBSCRIPTION_CHANNEL_ID, text, parse_mode='HTML')


async def sendError(text):
    await bot.send_message(constants.ERROR_CHANNEL_ID, text, parse_mode='HTML')
