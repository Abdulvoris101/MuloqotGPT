from utils import constants
from apps.subscription.managers import SubscriptionManager, FreeApiKeyManager
from apps.core.managers import MessageStatManager
import asyncio
from celery import Celery


celery = Celery('tasks', broker=constants.REDIS_URL, backend=constants.REDIS_URL)

celery.autodiscover_tasks()


@celery.task
def cancelExpiredSubscriptions():
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SubscriptionManager.cancelExpiredSubscriptions())
    
    return {"status": True}


@celery.task
def unsetExpiredKeys():
    FreeApiKeyManager.unExpireKeys()
        
    return {"status": True}


@celery.task
def clearAllTodaysMessages():
    MessageStatManager.clearAllUsersTodaysMessagesAndImages()
    
    return {"status": True}
    