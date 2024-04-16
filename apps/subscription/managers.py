from aiogram import types
from sqlalchemy import exists

from utils.events import sendEvent, sendError
from utils.exception import AiogramException
from .models import Subscription, Plan, FreeApiKey, Configuration, ChatQuota
import datetime
from db.setup import session
from utils import text
from utils import constants
from apps.core.managers import ChatActivityManager
from bot import bot
from ..core.models import ChatActivity


class PlanManager:
    
    @staticmethod
    def get(planId):
        return session.query(Plan).filter_by(id=planId).first()

    @staticmethod
    def getFreePlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=True).first()

        if plan is not None:
            return plan

        freePlan = Plan(
            title="Free plan",
            amountForMonth=0,
            monthlyLimitedGptRequests=constants.FREE_GPT_REQUESTS_MONTHLY,
            monthlyLimitedImageRequests=constants.FREE_IMAGEAI_REQUESTS_MONTHLY,
            isFree=True,
            isGroup=False,
            isHostGroup=False
        )

        session.add(freePlan)
        session.commit()

        return freePlan

    @staticmethod
    def getHostGroupPlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=False, isGroup=True,
                                             isHostGroup=True).first()
        
        if plan is not None:
            return plan

        groupHostPlan = Plan(
            title="Host Group plan",
            amountForMonth=constants.HOST_GROUP_PRICE,
            monthlyLimitedGptRequests=constants.GROUP_HOST_GPT_REQUESTS_MONTHLY,
            monthlyLimitedImageRequests=constants.GROUP_HOST_IMAGEAI_REQUESTS_MONTHLY,
            isFree=False,
            isGroup=True,
            isHostGroup=True
        )

        session.add(groupHostPlan)
        session.commit()

        return groupHostPlan

    @staticmethod
    def getPremiumPlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=False, isHostGroup=False,
                                             isGroup=False).first()
        
        if plan is not None:
            return plan

        premiumPlan = Plan(
            title="Premium plan",
            amountForMonth=constants.PREMIUM_PRICE,
            monthlyLimitedGptRequests=constants.PREMIUM_GPT_REQUESTS_MONTHLY,
            monthlyLimitedImageRequests=constants.PREMIUM_IMAGEAI_REQUESTS_MONTHLY,
            isFree=False,
            isGroup=False,
            isHostGroup=False
        )

        session.add(premiumPlan)
        session.commit()

        return premiumPlan

    @staticmethod
    def getFreePlanUsers():
        free_plan = PlanManager.getFreePlanOrCreate()
        
        free_subscription_users = session.query(Subscription).filter(
            Subscription.planId == free_plan.id, Subscription.is_paid == True,
            Subscription.isCanceled == False).all()
        
        return free_subscription_users

    @classmethod
    def getHostPlanId(cls):
        return cls.getHostGroupPlanOrCreate().id

    @classmethod
    def getFreePlanId(cls):
        return cls.getFreePlanOrCreate().id

    @classmethod
    def getPremiumPlanId(cls):
        return cls.getPremiumPlanOrCreate().id


class SubscriptionManager:
    @classmethod
    def getCurrentPeriodEnd(cls):
        """Compute the end of the current period."""
        return datetime.datetime.now() + datetime.timedelta(days=30)

    @classmethod
    def checkAndReactivate(cls, chatId, isFree):
        """Check if a subscription can be reactivated based on its status."""
        if isFree:
            return cls.reactivateFreeSubscription(chatId)
        return False

    @classmethod
    def createSubscription(
            cls, planId,
            chatId, cardholder=None,
            is_paid=False, isFree=True
    ):

        if cls.checkAndReactivate(chatId=chatId, isFree=isFree):
            return

        subscription = Subscription(
            planId=planId,
            currentPeriodStart=datetime.datetime.now(),
            currentPeriodEnd=None if isFree else cls.getCurrentPeriodEnd(),
            is_paid=is_paid,
            chatId=chatId,
            cardholder=cardholder
        )
        subscription.save()
        return subscription

    @staticmethod
    def unsubscribe(planId: int, chatId: int):
        subscription = session.query(Subscription).filter_by(chatId=chatId, planId=planId).first()

        if subscription is None:
            return

        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False
        subscription.isCanceled = True

        session.add(subscription)
        session.commit()

    @classmethod
    def subscribe(cls, planId: int, chatId: int):
        subscription = cls.getInActiveSubscription(chatId=chatId, planId=planId)
        subscription.isCanceled = False
        subscription.is_paid = True

        session.add(subscription)
        session.commit()

    @classmethod
    def reactivateFreeSubscription(cls, chatId: int) -> bool:
        inactiveSubscription = cls.filterSubscription(chatId=chatId, planId=PlanManager.getFreePlanId(),
                                                      isCanceled=True, isPaid=False)
        if inactiveSubscription is not None:
            inactiveSubscription.is_paid = True
            inactiveSubscription.isCanceled = False
            inactiveSubscription.canceledAt = None
            session.commit()
            return True

        return False

    @classmethod
    async def cancelExpiredSubscriptions(cls):
        subscriptions = session.query(Subscription).filter(
            Subscription.is_paid == True,
            Subscription.isCanceled == False,
            Subscription.planId == PlanManager.getPremiumPlanId(),
            Subscription.currentPeriodEnd < datetime.datetime.now()
        ).all()

        for subscription in subscriptions:
            subscription.isCanceled = True
            subscription.is_paid = False
            subscription.canceledAt = datetime.datetime.now()

            try:
                await bot.send_message(subscription.chatId, text.SUBSCRIPTION_END)
            except Exception as e:
                await sendError(f"<b>#subscription end can not send</b>\n{str(e)}\n\n#user {subscription.chatId}")

        session.commit()

    @classmethod
    def isPremiumToken(cls, chatId: int) -> bool:
        return any([
            cls.getActiveSubscription(chatId, PlanManager.getPremiumPlanId()),
            cls.getActiveSubscription(chatId, PlanManager.getHostPlanId()),
            ChatActivity.getOrCreate(chatId).allMessages < 3
        ])

    @classmethod
    def rejectPremiumRequest(cls, chatId: int):
        subscription = cls.getActiveSubscription(chatId=chatId, planId=PlanManager.getPremiumPlanId())

        if subscription is not None:
            raise AiogramException(userId=chatId, message_text="Foydalanuvchi allaqachon premium egasi")

        subscription.isCanceled = True
        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False

        session.add(subscription)
        session.commit()

    @classmethod
    def filterSubscription(cls, chatId: int, planId: int, isPaid: bool, isCanceled: bool):
        return session.query(Subscription).filter_by(chatId=chatId, is_paid=isPaid, isCanceled=isCanceled,
                                                     planId=planId).first()

    @classmethod
    def getActiveSubscription(cls, chatId: int, planId: int):
        return cls.filterSubscription(chatId=chatId, planId=planId,
                                      isCanceled=False, isPaid=True)

    @classmethod
    def getInActiveSubscription(cls, chatId: int, planId: int):
        return cls.filterSubscription(chatId=chatId, planId=planId,
                                      isPaid=False, isCanceled=False)

    @classmethod
    def getPremiumUsersCount(cls):
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanId(),
                                                     isCanceled=False, is_paid=True).count()

    @classmethod
    def getChatCurrentSubscription(cls, chatId: int):
        return session.query(Subscription).filter_by(
            chatId=chatId, is_paid=True, isCanceled=False
        ).first() or SubscriptionManager.createSubscription(
            planId=PlanManager.getFreePlanId(), chatId=chatId, cardholder=None, is_paid=True,
            isFree=True
        )


class LimitManager:
    @classmethod
    def getUsedRequestsToday(cls, chatId: int, messageType: str):
        chatActivity = ChatActivity.getOrCreate(chatId=chatId)
        if messageType == "GPT":
            return chatActivity.todaysMessages
        elif messageType == "IMAGE":
            return chatActivity.todaysImages

    @classmethod
    def getDailyRequestLimit(cls, chatId: int, messageType: str) -> int:
        userSubscription = SubscriptionManager.getChatCurrentSubscription(chatId=chatId)
        keys = {"GPT": "monthlyLimitedGptRequests", "IMAGE": "monthlyLimitedImageRequests"}
        userPlan = PlanManager.get(userSubscription.planId)
        limitKey = keys.get(messageType)
        return getattr(userPlan, limitKey, 0) // 30

    @classmethod
    def checkRequestsDailyLimit(cls, chatId: int, messageType: str) -> bool:
        planLimit = cls.getDailyRequestLimit(chatId, messageType)
        chatUsedRequests = cls.getUsedRequestsToday(chatId, messageType)
        chatQuota = ChatQuota.getOrCreate(chatId)

        additionalKeys = {"GPT": "additionalGptRequests", "IMAGE": "additionalImageRequests"}

        if planLimit > chatUsedRequests:
            return True

        key = additionalKeys.get(messageType)

        if getattr(chatQuota, key, 0) > 0:
            cls.decrementQuota(chatQuota, key)
            return True

        return False

    @classmethod
    def decrementQuota(cls, chatQuota: ChatQuota, key: str):
        """Decrement the specified key for additional requests in the chat quota."""
        if getattr(chatQuota, key, 0) > 0:
            setattr(chatQuota, key, getattr(chatQuota, key) - 1)
            session.commit()


class FreeApiKeyManager:
    
    @staticmethod
    def getApiKey(index: int) -> FreeApiKey:
        freeApiKeys = session.query(FreeApiKey).filter_by(isExpired=False).all()

        if index < len(freeApiKeys):
            return freeApiKeys[index]

        raise IndexError("")

    @staticmethod
    def getTotalActiveKeysCount() -> int:
        return session.query(FreeApiKey).filter_by(isExpired=False).count()

    @staticmethod
    def incrementRequest(apiKeyId: int) -> None:
        """Increment the request count for a specific API key."""
        freeApiKey = session.query(FreeApiKey).filter_by(id=apiKeyId).first()

        freeApiKey.requests += 1
        if freeApiKey.requests >= 200:
            freeApiKey.isExpired = True
        session.commit()

    @staticmethod
    def reactivateAllKeys():
        session.query(FreeApiKey).update({
            FreeApiKey.isExpired: False,
            FreeApiKey.requests: 0
        })
        session.commit()


class ConfigurationManager:
    
    @staticmethod
    def getConfigs():
        configuration = session.query(Configuration).first()
        
        if configuration is None:
            configuration = Configuration(apikeyPosition=0)
            configuration.save()
        
        return configuration
    
    @staticmethod
    def updatePosition(
        number
    ):
        configuration = session.query(Configuration).first()
        configuration.apikeyPosition = number
        session.add(configuration)
        session.commit()
        return configuration


