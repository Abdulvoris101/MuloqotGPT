# tasks.py
import asyncio

from apps.core.managers import ChatActivityManager
from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager


def cancelExpiredSubscriptions():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionManager.cancelExpiredSubscriptions())

    print("Canceled Expired Subscriptions!")


def unsetExpiredKeys():
    FreeApiKeyManager.unExpireKeys()

    print("unsetExpiredKeys")


def clearAllTodaysMessages():
    ChatActivityManager.clearAllUsersTodayMessagesAndImages()

    print("clearedAllTodaysMessages")