# tasks.py
import asyncio

from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager
from bot import logger


async def cancelExpiredSubscriptions():
    await SubscriptionManager.cancelExpiredSubscriptions()

    logger.info("Canceled Expired Subscriptions!")


def unsetExpiredKeys():
    FreeApiKeyManager.reactivateAllKeys()

    logger.info("Reactivate all keys!")
