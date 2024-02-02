# tasks.py
from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager
from apps.core.managers import ChatActivityManager


import asyncio

def say_hello():
    print("hello")

def cancelExpiredSubscriptions():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionManager.cancelExpiredSubscriptions())
    
    print("Canceled Expired Subscriptions!")


def unsetExpiredKeys():
    FreeApiKeyManager.unExpireKeys()
    
    print("unsetExpiredKeys")

def clearAllTodaysMessages():
    ChatActivityManager.clearAllUsersTodaysMessagesAndImages()
    

    print("clearedAllTodaysMessages")
    