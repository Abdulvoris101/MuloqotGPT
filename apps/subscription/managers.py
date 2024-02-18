from .models import Subscription, Plan, FreeApiKey, Configuration, ChatQuota
import datetime
from db.setup import session
from utils import text
from utils import constants
from apps.core.managers import ChatActivityManager
from sqlalchemy import not_
from bot import bot
from apps.core.models import Chat

class SubscriptionManager:


    @classmethod
    def createSubscription(
        cls,
        planId,
        chatId,
        cardholder=None,
        is_paid=False,
        isFree=True
    ):
        
        if isFree:
            isActivated = cls.reactivateFreeSubscription(chatId)

            if isActivated:
                return
        
        
        currentPeriodEnd = datetime.datetime.now() + datetime.timedelta(days=30)

        subscription = Subscription(
            planId=planId,
            currentPeriodStart=datetime.datetime.now(),
            currentPeriodEnd=None if isFree else currentPeriodEnd,
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
        chat_subscription = SubscriptionManager.getByChatId(chatId=chatId)

        if chat_subscription is None:
            if isFree:
                isActivated = cls.reactivateFreeSubscription(chatId)

                if isActivated:
                    return

            currentPeriodEnd = datetime.datetime.now() + datetime.timedelta(days=30)

            subscription = Subscription(
                planId=planId,
                currentPeriodStart=datetime.datetime.now(),
                currentPeriodEnd=None if isFree else currentPeriodEnd,
                is_paid=is_paid,
                chatId=chatId,
                cardholder=cardholder
            )

            session.add(subscription)
            session.commit()

            return subscription

        return chat_subscription
    

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
        inactive_subscription = cls.getUsersFreeInactiveSubscription(chatId)

        if inactive_subscription is not None:
            inactive_subscription.is_paid = True
            inactive_subscription.isCanceled = False
            inactive_subscription.canceledAt = None

            session.add(inactive_subscription) # set active the free subscription
            session.commit()

            return True
        
        return False
    

    @staticmethod
    async def cancelExpiredSubscriptions():
        
        subscriptions_to_cancel = session.query(Subscription).filter(
            Subscription.is_paid == True,
            Subscription.isCanceled == False,
            Subscription.planId == PlanManager.getPremiumPlanOrCreate().id,
            Subscription.currentPeriodEnd < datetime.datetime.now()
        ).all()
        
        for subscription in subscriptions_to_cancel:
            subscription.isCanceled = True
            subscription.is_paid = False
            subscription.canceledAt = datetime.datetime.now()
            session.add(subscription)
            
            await bot.send_message(subscription.chatId, text.SUBSCRIPTION_END)

        # Commit the changes to the database
        session.commit()
        
    
    @classmethod
    def isPremiumToken(cls, chatId):
        subscription = cls.getPremiumSubscription(chatId=chatId, 
                                  planId=PlanManager.getPremiumPlanOrCreate().id)
        
        group_subscription = cls.getHostGroupSubscription(chatId=chatId, 
                                  planId=PlanManager.getHostGroupPlanOrCreate().id)
        
        users_used_requests = ChatActivityManager.getAllMessagesCount(chatId)

        if subscription is not None:
            return True
        elif group_subscription is not None:
            return True
        elif users_used_requests < 10:
            return True
        

        return False
    
    @classmethod
    def rejectPremiumRequest(cls, chatId):
        subscription = cls.getInActivePremiumSubscription(
            chatId=chatId,
            planId=PlanManager.getPremiumPlanOrCreate().id
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
            chatId=chatId, planId=PlanManager.getFreePlanOrCreate().id, is_paid=False, isCanceled=True).first()
        
    
        
    @staticmethod
    def findByChatIdAndPlanId(
        chatId,
        planId
    ):
        return session.query(Subscription).filter_by(chatId=chatId, planId=planId).first()


    @staticmethod
    def getNotPaidPremiumSubscription(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, is_paid=False, isCanceled=False).first()


    @staticmethod
    def getPremiumSubscription(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, isCanceled=False, is_paid=True).first()

    @staticmethod
    def getHostGroupSubscription(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, isCanceled=False, is_paid=True).first()


    @staticmethod
    def getInActivePremiumSubscription(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, is_paid=False, isCanceled=False).first()

    
    @staticmethod
    def getByChatId(
        chatId
    ):
        return session.query(Subscription).filter_by(chatId=chatId).first()

    @staticmethod
    def getPremiumUsersCount():
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanOrCreate().id, isCanceled=False, is_paid=True).count()
    
        

class LimitManager:
     
    @classmethod
    def checkGptRRequestsDailyLimit(cls, chatId):
        chat_plan_limit = cls.getDailyGptLimitOfUser(chatId)
        chat_used_requests = ChatActivityManager.getTodaysMessage(chatId)
        chat_quota = ChatQuota.get(chatId)
        chatRecord = Chat.get(chatId)
        
        if chat_quota is None:
            if chatRecord is not None:
                ChatQuota(
                    chatId=chatId, additionalGptRequests=0,
                    additionalImageRequests=0).save()
        
        chatQuota = ChatQuota.get(chatId)
        
        if chat_plan_limit > chat_used_requests:
            return True
        elif chatQuota.additionalGptRequests > 1:
            if chatRecord is not None:
                ChatQuota.update(chatQuota, "additionalGptRequests", chatQuota.additionalGptRequests - 1)
            return True
        
        return False
    
    @classmethod
    def checkImageaiRequestsDailyLimit(cls, chatId):
        chat_plan_limit = cls.getDailyImageAiLimitOfUser(chatId)
        chat_used_requests = ChatActivityManager.getTodayImages(chatId)
        chat_quota = ChatQuota.get(chatId)
        
        if chat_quota is None:
            ChatQuota(
                chatId=chatId, additionalGptRequests=0,
                additionalImageRequests=0).save()
            
        chatQuota = ChatQuota.get(chatId)
        
        if chat_plan_limit > chat_used_requests:
            return True
        elif chatQuota.additionalImageRequests > chat_used_requests:
            ChatQuota.update(chatQuota, "additionalImageRequests", chatQuota.additionalImageRequests - 1)
            return True
        
        return False

    @classmethod
    def dailyLimitOfUser(cls):
        cls.free_plan = PlanManager.getFreePlanOrCreate()
        cls.premium_plan = PlanManager.getPremiumPlanOrCreate()
        cls.host_group_plan = PlanManager.getHostGroupPlanOrCreate()
        
        cls.premium_subscription = session.query(Subscription).filter_by(
            chatId=cls.chatId, planId=cls.premium_plan.id, is_paid=True, isCanceled=False).first()
        
        cls.free_subscription = session.query(Subscription).filter_by(
            chatId=cls.chatId, planId=cls.free_plan.id, is_paid=True, isCanceled=False).first()
        
        cls.host_group_subscription = session.query(Subscription).filter_by(
            chatId=cls.chatId, planId=cls.host_group_plan.id, is_paid=True, isCanceled=False).first()
        
    
    @classmethod
    def getDailyGptLimitOfUser(
        cls,       
        chatId
    ):
        cls.chatId = int(chatId)
        
        
        cls.dailyLimitOfUser()
        
        if cls.premium_subscription is not None:
            return int(cls.premium_plan.monthlyLimitedGptRequests) / 30 # get daily limit requests
        elif cls.free_subscription is not None:
            return int(cls.free_plan.monthlyLimitedGptRequests) / 30
        elif cls.host_group_subscription is not None:
            return int(cls.host_group_plan.monthlyLimitedGptRequests) / 30
        
        elif chatId == constants.HOST_GROUP_ID and cls.host_group_subscription is None:
            SubscriptionManager.createSubscription(
                planId=cls.host_group_plan.id,
                chatId=chatId,
                cardholder="ABDUVORIS ERKINOV",
                is_paid=True,
                isFree=False
            )
            return int(cls.host_group_plan.monthlyLimitedGptRequests) / 30
        
        else:
            SubscriptionManager.createSubscription(
                planId=cls.free_plan.id,
                chatId=chatId,
                cardholder=None,
                is_paid=True,
                isFree=True
            )

            return int(cls.free_plan.monthlyLimitedGptRequests) / 30
    
    
    @classmethod
    def getDailyImageAiLimitOfUser(
        cls,       
        chatId
    ):
        cls.chatId = chatId

        cls.dailyLimitOfUser()
        
        if cls.premium_subscription is not None:
            return int(cls.premium_plan.monthlyLimitedImageRequests) / 30 # get daily limit requests
        elif cls.free_subscription is not None:
            return int(cls.free_plan.monthlyLimitedImageRequests) / 30
        
        elif cls.host_group_subscription is not None:
            return int(cls.host_group_plan.monthlyLimitedGptRequests) / 30
        
        elif chatId == constants.HOST_GROUP_ID and cls.host_group_subscription is None:
            SubscriptionManager.createSubscription(
                planId=cls.host_group_plan.id,
                chatId=chatId,
                cardholder="ABDUVORIS ERKINOV",
                is_paid=True,
                isFree=False
            )
            return int(cls.host_group_plan.monthlyLimitedGptRequests) / 30
        else:
            SubscriptionManager.createSubscription(
                planId=cls.free_plan.id,
                chatId=chatId,
                cardholder=None,
                is_paid=True,
                isFree=True
            )

            return int(cls.free_plan.monthlyLimitedImageRequests) / 30


class PlanManager:
    
    @staticmethod
    def get(planId):
        return session.query(Plan).filter_by(id=planId)

    
    @staticmethod
    def getFreePlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=True).first()
        
        if plan is None:
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
        
        return plan

    @staticmethod
    def getHostGroupPlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=False, isGroup=True, isHostGroup=True).first()
        
        if plan is None:
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
        
        return plan


    @staticmethod
    def getPremiumPlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=False, isHostGroup=False, isGroup=False).first()
        
        if plan is None:
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
        
        return plan


    @staticmethod
    def getFreePlanUsers():
        free_plan = PlanManager.getFreePlanOrCreate()
        
        free_subscription_users = session.query(Subscription).filter(
            Subscription.planId == free_plan.id, Subscription.is_paid == True, 
            Subscription.isCanceled==False).all()
        
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
    

