from typing import List, Optional
from uuid import UUID

from aiogram.exceptions import TelegramNotFound
from sqlalchemy import or_, exists, desc
from apps.common.exception import AiogramException
from .models import Subscription, Plan, FreeApiKey, Configuration, ChatQuota, Limit
import datetime
from db.setup import session
from utils import text
from bot import bot, logger
from ..core.managers import MessageManager, ChatActivityManager
from ..core.models import ChatActivity


class PlanManager:
    
    @staticmethod
    def get(planId: UUID) -> Plan:
        return session.query(Plan).filter_by(id=planId).first()

    @staticmethod
    def isExistsById(planId: UUID) -> Plan:
        return session.query(exists().where(Plan.id == planId)).scalar()

    @classmethod
    def filterPlan(cls, isFree: bool, isGroup: bool):
        return session.query(Plan).filter_by(isFree=isFree, isGroup=isGroup).order_by(
            desc(Plan.amountForMonth)).first()

    @classmethod
    def filterPlans(cls, isFree: bool, isGroup: bool):
        return session.query(Plan).filter_by(isFree=isFree, isGroup=isGroup).all()

    @staticmethod
    def getFreePlanUsers() -> List[Subscription]:
        freePlanId = PlanManager.getFreePlanId()
        groupPlanId = PlanManager.filterPlan(isFree=False, isGroup=True).id

        freeUsers = session.query(Subscription).filter(
            or_(
                Subscription.planId == freePlanId,
                Subscription.planId == groupPlanId
            ),
            Subscription.is_paid == True, Subscription.isCanceled == False).all()
        
        return freeUsers

    @classmethod
    def getFreePlanId(cls) -> UUID:
        return cls.filterPlan(isFree=True, isGroup=False).id

    @classmethod
    def getPremiumPlanId(cls) -> UUID:
        return cls.filterPlan(isFree=False, isGroup=False).id

    @classmethod
    def getSubscriptionPlans(cls):
        return session.query(Plan).filter_by(isGroup=False).order_by(Plan.id).all()

    @classmethod
    def excludePlan(cls, planId: UUID):
        return session.query(Plan).filter(Plan.id != planId).all()


class SubscriptionManager:
    @classmethod
    def getCurrentPeriodEnd(cls):
        """Compute the end of the current period."""
        return datetime.datetime.now() + datetime.timedelta(days=30)

    @classmethod
    def createSubscription(cls, planId: UUID, chatId: int, is_paid=False):
        subscription = Subscription(
            planId=planId,
            currentPeriodStart=datetime.datetime.now(),
            currentPeriodEnd=cls.getCurrentPeriodEnd(),
            is_paid=is_paid,
            chatId=chatId
        )

        subscription.save()
        return subscription

    @staticmethod
    def unsubscribe(planId: UUID, chatId: int):
        subscription = session.query(Subscription).filter_by(chatId=chatId, planId=planId).first()

        if subscription is None:
            return

        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False
        subscription.isCanceled = True

        session.add(subscription)
        session.commit()

    @staticmethod
    def bulkUnsubscribe(plans: List[Plan], chatId: int):
        subscriptionQuery = session.query(Subscription) \
            .filter(Subscription.chatId == chatId, Subscription.planId.in_([plan.id for plan in plans]))

        subscriptionQuery.update({
            Subscription.canceledAt: datetime.datetime.now(),
            Subscription.is_paid: False,
            Subscription.isCanceled: True
        }, synchronize_session=False)

        session.commit()

    @classmethod
    def subscribe(cls, planId: UUID, chatId: int):
        subscription = cls.getInActiveSubscription(chatId=chatId, planId=planId)
        subscription.isCanceled = False
        subscription.is_paid = True

        session.add(subscription)
        session.commit()

    @classmethod
    async def cancelExpiredSubscriptions(cls):
        notIncludePlanId = PlanManager.filterPlan(isGroup=True, isFree=False).id # group ids

        subscriptions = session.query(Subscription).filter(
            Subscription.is_paid == True,
            Subscription.isCanceled == False,
            Subscription.planId != notIncludePlanId,
            Subscription.currentPeriodEnd < datetime.datetime.now()
        ).all()

        for subscription in subscriptions:
            ChatActivityManager.cleanActivityCounts(subscription.chatId)
            subscription.isCanceled = True
            subscription.is_paid = False
            subscription.canceledAt = datetime.datetime.now()

            try:
                if subscription.planId != PlanManager.getFreePlanId():
                    await bot.send_message(subscription.chatId, text.SUBSCRIPTION_END)
            except TelegramNotFound as e:
                logger.error("User not found")

        session.commit()

    @classmethod
    def isPremiumToken(cls, chatId: int) -> bool:
        return any([
            cls.getActiveSubscription(chatId, PlanManager.getPremiumPlanId()),
            cls.getActiveSubscription(chatId, PlanManager.filterPlan(isFree=False, isGroup=True).id),
            ChatActivity.getOrCreate(chatId).allMessages < 10
        ])

    @classmethod
    def rejectPremiumRequest(cls, chatId: int):
        premiumSubscription = cls.getActiveSubscription(chatId=chatId,
                                                        planId=PlanManager.getPremiumPlanId())

        inactivePremiumSubscription = cls.filterSubscription(chatId=chatId, isPaid=False, isCanceled=False,
                                                             planId=PlanManager.getPremiumPlanId())

        if premiumSubscription is not None:
            raise AiogramException(userId=chatId, message_text="Foydalanuvchi allaqachon premium egasi")
        elif inactivePremiumSubscription is None:
            raise AiogramException(userId=chatId, message_text="Foydalanuvchi premiumga so'rov yubormagan!")

        inactivePremiumSubscription.isCanceled = True
        inactivePremiumSubscription.canceledAt = datetime.datetime.now()
        inactivePremiumSubscription.is_paid = False

        session.add(inactivePremiumSubscription)
        session.commit()

    @classmethod
    def filterSubscription(cls, chatId: int, planId: UUID, isPaid: bool, isCanceled: bool):
        return session.query(Subscription).filter_by(chatId=chatId, is_paid=isPaid, isCanceled=isCanceled,
                                                     planId=planId).first()

    @classmethod
    def getActiveSubscription(cls, chatId: int, planId: UUID):
        return cls.filterSubscription(chatId=chatId, planId=planId,
                                      isCanceled=False, isPaid=True)

    @classmethod
    def getInActiveSubscription(cls, chatId: int, planId: UUID):
        return cls.filterSubscription(chatId=chatId, planId=planId,
                                      isPaid=False, isCanceled=False)

    @classmethod
    def getPremiumUsersCount(cls) -> int:
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanId(),
                                                     isCanceled=False, is_paid=True).count()

    @classmethod
    def getChatCurrentSubscription(cls, chatId: int) -> Subscription:
        currentSubscription = session.query(Subscription).filter_by(
            chatId=chatId, is_paid=True, isCanceled=False
        ).first()

        return currentSubscription

    @classmethod
    def getCurrentSubscriptionOrCreate(cls, chatId: int) -> None:
        currentSubscription = cls.getChatCurrentSubscription(chatId=chatId)

        if currentSubscription is None:
            SubscriptionManager.createSubscription(planId=PlanManager.getFreePlanId(),
                                                   chatId=chatId, is_paid=True)


class LimitManager:
    @classmethod
    def getUsedRequests(cls, chatId: int, messageType: str, model: str, subscription: Subscription):
        return MessageManager.getUserMessagesTimeFrame(chatId=chatId, days=31,
                                                       messageType=messageType, model=model,
                                                       subscription=subscription)

    @classmethod
    def getPlanLimits(cls, model: str, subscription: Subscription) -> int:
        keys = {"gpt-3.5-turbo-0125": "monthlyLimitGpt3",
                "gpt-4": "monthlyLimitGpt4",
                "lexica": "monthlyLimitImage"}

        plan = PlanManager.get(subscription.planId)
        limit = Limit.get(plan.limitId)
        limitKey = keys.get(model)

        return getattr(limit, limitKey, 0)

    @classmethod
    def hasQuotaExceeded(cls, chatId: int, messageType: str, model: str) -> bool:
        subscription = SubscriptionManager.getChatCurrentSubscription(chatId=chatId)
        limitedRequests = cls.getPlanLimits(model=model, subscription=subscription)
        usedRequests = cls.getUsedRequests(chatId=chatId, messageType=messageType, model=model,
                                           subscription=subscription)
        chatQuota = ChatQuota.getOrCreate(chatId)

        additionalKeys = {"gpt-3.5-turbo-0125": "additionalGpt3Requests",
                          "gpt-4": "additionalGpt4Requests",
                          "lexica": "additionalImageRequests"}

        if limitedRequests > usedRequests:
            return False

        key = additionalKeys.get(model)

        if getattr(chatQuota, key, 0) > 0:
            cls.decrementQuota(chatQuota, key)
            return False

        return True

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
    def getConfigs() -> Configuration:
        configuration = session.query(Configuration).first()
        
        if configuration is None:
            configuration = Configuration(apikeyPosition=0)
            configuration.save()
        
        return configuration
    
    @staticmethod
    def updatePosition(number) -> Configuration:
        configuration = session.query(Configuration).first()
        configuration.apikeyPosition = number
        session.add(configuration)
        session.commit()
        return configuration


class ChatQuotaManager:
    @staticmethod
    def incrementCount(chatId: int, column: str, value: int) -> None:
        instance = ChatQuota.get(chatId=chatId)
        currentValue = getattr(instance, column)

        ChatQuota.update(instance, column, int(currentValue) + value)
