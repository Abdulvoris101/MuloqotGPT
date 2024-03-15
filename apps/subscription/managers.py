from utils.exception import AiogramException
from .models import Subscription, Plan, FreeApiKey, Configuration, ChatQuota
import datetime
from db.setup import session
from utils import text
from utils import constants
from apps.core.managers import ChatActivityManager
from ..core.models import Chat
from bot import bot


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
    currentPeriodEnd = datetime.datetime.now() + datetime.timedelta(days=30)

    @classmethod
    def checkAndReactivate(cls, chatId, isFree):
        if isFree:
            isActivated = cls.reactivateFreeSubscription(chatId)
            if isActivated:
                return True
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
            currentPeriodEnd=None if isFree else cls.currentPeriodEnd,
            is_paid=is_paid,
            chatId=chatId,
            cardholder=cardholder
        )

        session.add(subscription)
        session.commit()

        return subscription

    @classmethod
    def getSubscriptionOrCreate(
            cls,
            planId,
            chatId,
            cardholder=None,
            is_paid=False,
            isFree=True
    ):
        chatSubscription = SubscriptionManager.getByChatId(chatId=chatId)

        if chatSubscription is not None:
            return chatSubscription

        if cls.checkAndReactivate(chatId=chatId, isFree=isFree):
            return

        subscription = Subscription(
            planId=planId,
            currentPeriodStart=datetime.datetime.now(),
            currentPeriodEnd=None if isFree else cls.currentPeriodEnd,
            is_paid=is_paid,
            chatId=chatId,
            cardholder=cardholder
        )

        session.add(subscription)
        session.commit()

        return subscription

    @staticmethod
    def unsubscribe(
            planId,
            chatId
    ):
        subscription = session.query(Subscription).filter_by(chatId=chatId, planId=planId).first()

        if subscription is None:
            return False

        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False
        subscription.isCanceled = True

        session.add(subscription)
        session.commit()
        return True

    @classmethod
    def subscribe(
            cls,
            planId,
            chatId
    ):
        subscription = cls.getInActivePremiumSubscription(
            chatId=chatId,
            planId=planId
        )

        subscription.isCanceled = False
        subscription.is_paid = True

        session.add(subscription)
        session.commit()

    @classmethod
    def reactivateFreeSubscription(cls, chatId):
        inactiveSubscription = cls.getUsersFreeInactiveSubscription(chatId)

        if inactiveSubscription is None:
            return False

        inactiveSubscription.is_paid = True
        inactiveSubscription.isCanceled = False
        inactiveSubscription.canceledAt = None

        session.add(inactiveSubscription)
        session.commit()

        return True

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
            session.add(subscription)

            await bot.send_message(subscription.chatId, text.SUBSCRIPTION_END)

        session.commit()

    @classmethod
    def isPremiumToken(cls, chatId):
        subscription = cls.getPremiumSubscription(chatId=chatId,
                                                  planId=PlanManager.getPremiumPlanId())

        group_subscription = cls.getHostGroupSubscription(chatId=chatId,
                                                          planId=PlanManager.getHostPlanId())

        users_used_requests = ChatActivityManager.getAllMessagesCount(chatId)

        if subscription is not None:
            return True
        elif group_subscription is not None:
            return True
        elif users_used_requests < 3:
            return True

        return False

    @classmethod
    def rejectPremiumRequest(cls, chatId):
        subscription = cls.getInActivePremiumSubscription(
            chatId=chatId,
            planId=PlanManager.getPremiumPlanId()
        )

        if subscription is None:
            return

        subscription.isCanceled = True
        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False

        session.add(subscription)
        session.commit()

    @classmethod
    def getUsersFreeInactiveSubscription(cls, chatId):
        return session.query(Subscription).filter_by(
            chatId=chatId, planId=PlanManager.getFreePlanId(), is_paid=False, isCanceled=True).first()

    @staticmethod
    def findByChatIdAndPlanId(
            chatId,
            planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId).first()

    @staticmethod
    def getUnpaidPremiumSubscription(
            chatId,
            planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId,
                                                     is_paid=False, isCanceled=False).first()

    @staticmethod
    def getPremiumSubscription(
            chatId,
            planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId,
                                                     isCanceled=False, is_paid=True).first()

    @staticmethod
    def getHostGroupSubscription(
            chatId,
            planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId,
                                                     isCanceled=False, is_paid=True).first()

    @staticmethod
    def getInActivePremiumSubscription(
            chatId,
            planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId,
                                                     is_paid=False, isCanceled=False).first()

    @staticmethod
    def getByChatId(
            chatId
    ):
        return session.query(Subscription).filter_by(chatId=chatId).first()

    @classmethod
    def getPremiumUsersCount(cls):
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanId(),
                                                     isCanceled=False, is_paid=True).count()

    @classmethod
    def getUserActiveSubscription(cls, chatId):
        userActiveSubscription = session.query(Subscription).filter_by(
            chatId=chatId, is_paid=True, isCanceled=False).first()

        return userActiveSubscription


class LimitManager:
    @classmethod
    def getUsedRequests(cls, chatId, messageType):
        if messageType == "GPT":
            return ChatActivityManager.getTodayMessagesCount(chatId)
        elif messageType == "IMAGE":
            return ChatActivityManager.getTodayImages(chatId)

    @classmethod
    def checkRequestsDailyLimit(cls, chatId, messageType):
        chatPlanLimit = cls.getDailyGptLimitOfUser(chatId, messageType)
        chatUsedRequests = cls.getUsedRequests(chatId, messageType)
        chatQuota = ChatQuota.getOrCreate(chatId)

        if chatPlanLimit > chatUsedRequests:
            return True

        elif chatQuota.additionalGptRequests >= 1 and messageType == "GPT":
            ChatQuota.update(chatQuota, "additionalGptRequests",
                             chatQuota.additionalGptRequests - 1)
            return True

        elif chatQuota.additionalImageRequests >= 1 and messageType == "IMAGE":
            ChatQuota.update(chatQuota, "additionalImageRequests",
                             chatQuota.additionalImageRequests - 1)

            return True

        return False

    @classmethod
    def getDailyGptLimitOfUser(
            cls,
            chatId,
            messageType
    ):
        userSubscription = SubscriptionManager.getUserActiveSubscription(chatId=chatId)

        if userSubscription is None:
            userSubscription = SubscriptionManager.createSubscription(
                planId=PlanManager.getFreePlanId(),
                chatId=chatId,
                cardholder=None,
                is_paid=True,
                isFree=True
            )

        userPlan = PlanManager.get(userSubscription.planId)

        if messageType == "GPT":
            return int(userPlan.monthlyLimitedGptRequests) / 30
        elif messageType == "IMAGE":
            return int(userPlan.monthlyLimitedImageRequests) / 30


class FreeApiKeyManager:
    
    @staticmethod
    def getApiKey(num):
        free_apiKeys = session.query(FreeApiKey).filter_by(isExpired=False).all()
        return free_apiKeys[num]

    @staticmethod
    def getMaxNumber():
        free_apiKeys = session.query(FreeApiKey).filter_by(isExpired=False).all()
        return len(free_apiKeys)
    
    @staticmethod
    def increaseRequest(id):
        free_apiKey = session.query(FreeApiKey).filter_by(id=id).first()

        free_apiKey.requests = free_apiKey.requests + 1

        session.add(free_apiKey)
        session.commit()

    @staticmethod
    def checkAndExpireKey(id):
        free_apiKey = session.query(FreeApiKey).filter_by(id=id).first()

        if free_apiKey.requests == 200:
            free_apiKey.isExpired = True

        session.add(free_apiKey)
        session.commit()

    @staticmethod
    def unExpireKeys():
        free_apiKeys = session.query(FreeApiKey).all()

        for free_apiKey in free_apiKeys:
            free_apiKey.isExpired = False
            free_apiKey.requests = 0

            session.add(free_apiKey)

        session.commit()


class ConfigurationManager:
    
    @staticmethod
    def getFirst():
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

    @staticmethod
    def setIsBetaTrue():
        configuration = session.query(Configuration).first()

        configuration.isBeta = True

        session.add(configuration)
        session.commit()

    @staticmethod
    def setIsBetaFalse():
        configuration = session.query(Configuration).first()

        configuration.isBeta = False

        session.add(configuration)
        session.commit()

