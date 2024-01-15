from celery import Celery
from utils import constants
from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager
from apps.core.managers import MessageStatManager
import asyncio

celery = Celery(
    'tasks',
    broker=constants.REDIS_URL,
    backend=constants.REDIS_URL,
)

@celery.task
def cancelExpiredSubscriptions():
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(SubscriptionManager.cancelExpiredSubscriptions())
    
    return {"status": True}


@celery.task
def unsetExpiredKeys():
    FreeApiKeyManager.unExpireKeys()
        
    return {"status": True}


@celery.task
def clearAllTodaysMessages():
    MessageStatManager.clearAllUsersTodaysMessagesAndImages()
    
    return {"status": True}
    