# tasks.py
import asyncio

from apps.core.managers import ChatActivityManager
from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager


async def cancelExpiredSubscriptions():
    await SubscriptionManager.cancelExpiredSubscriptions()

    print("Canceled Expired Subscriptions!")


def unsetExpiredKeys():
    FreeApiKeyManager.unExpireKeys()

    print("unsetExpiredKeys")


def clearAllTodaysMessages():
    ChatActivityManager.resetTodayCounters()

    print("clearedAllTodaysMessages")