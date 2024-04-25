from typing import List

from aiogram.exceptions import TelegramNotFound
from sqlalchemy import or_
from apps.common.exception import AiogramException
from .models import Subscription, Plan, FreeApiKey, Configuration, ChatQuota, Limit
import datetime
from db.setup import session
from utils import text
from bot import bot, logger
from ..core.managers import MessageManager
from ..core.models import ChatActivity


class PlanManager:
    
    @staticmethod
    def get(planId: int) -> Plan:
        return session.query(Plan).filter_by(id=planId).first()

    @staticmethod
    def getFreePlan() -> Plan:
        return session.query(Plan).filter_by(isFree=True).first()

    @staticmethod
    def getHostGroupPlan() -> Plan:
        return session.query(Plan).filter_by(isFree=False, isGroup=True).first()

    @staticmethod
    def getPremiumPlan() -> Plan:
        return session.query(Plan).filter_by(isFree=False, isGroup=False).first()

    @staticmethod
    def getFreePlanUsers() -> List[Subscription]:
        freePlanId = PlanManager.getFreePlanId()
        groupPlanId = PlanManager.getHostPlanId()

        freeUsers = session.query(Subscription).filter(
            or_(
                Subscription.planId == freePlanId,
                Subscription.planId == groupPlanId
            ),
            Subscription.is_paid == True, Subscription.isCanceled == False).all()
        
        return freeUsers

    @classmethod
    def getHostPlanId(cls) -> int:
        return cls.getHostGroupPlan().id

    @classmethod
    def getFreePlanId(cls) -> int:
        return cls.getFreePlan().id

    @classmethod
    def getPremiumPlanId(cls) -> int:
        return cls.getPremiumPlan().id


class SubscriptionManager:
    @classmethod
    def getCurrentPeriodEnd(cls):
        """Compute the end of the current period."""
        return datetime.datetime.now() + datetime.timedelta(days=30)

    @classmethod
    def checkAndReactivate(cls, chatId: int, isFree: bool):
        """Check if a subscription can be reactivated based on its status."""
        if isFree:
            return cls.reactivateFreeSubscription(chatId)
        return False

    @classmethod
    def createSubscription(cls, planId: int, chatId: int, cardholder=None, is_paid=False,
                           isFree=True):

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
            except TelegramNotFound as e:
                logger.error("User not found")

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
    def getPremiumUsersCount(cls) -> int:
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanId(),
                                                     isCanceled=False, is_paid=True).count()

    @classmethod
    def getChatCurrentSubscription(cls, chatId: int) -> Subscription:
        currentSubscription = session.query(Subscription).filter_by(
            chatId=chatId, is_paid=True, isCanceled=False
        ).first()

        if currentSubscription is None:
            currentSubscription = SubscriptionManager.createSubscription(
                planId=PlanManager.getFreePlanId(), chatId=chatId, cardholder=None, is_paid=True,
                isFree=True
            )
        return currentSubscription


class LimitManager:
    @classmethod
    def getUsedRequests(cls, chatId: int, messageType: str):
        if messageType == "GPT":
            return MessageManager.getUserMessagesTimeFrame(chatId=chatId, days=31,
                                                           messageType="message")
        elif messageType == "IMAGE":
            return MessageManager.getUserMessagesTimeFrame(chatId=chatId, days=31,
                                                           messageType="image")

    @classmethod
    def getUserRequestLImit(cls, chatId: int, messageType: str) -> int:
        userSubscription = SubscriptionManager.getChatCurrentSubscription(chatId=chatId)
        keys = {"GPT": "monthlyLimitedGptRequests", "IMAGE": "monthlyLimitedImageRequests"}
        userPlan = PlanManager.get(userSubscription.planId)
        planLimit = Limit.get(userPlan.limitId)
        limitKey = keys.get(messageType)
        return getattr(planLimit, limitKey, 0)

    @classmethod
    def checkRequestsDailyLimit(cls, chatId: int, messageType: str) -> bool:
        planLimit = cls.getUserRequestLImit(chatId, messageType)
        chatUsedRequests = cls.getUsedRequests(chatId, messageType)
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


