from .models import Subscription, Plan, FreeApiKey, Configuration
import datetime
from db.setup import session
from utils import text
from utils import constants
from apps.core.managers import MessageStatManager
from sqlalchemy import not_
from bot import bot

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
        subscription = cls.getInActivePremiumSubsctiption(
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
        subscription = cls.getPremiumSubsctiption(chatId=chatId, 
                                  planId=PlanManager.getPremiumPlanOrCreate().id)
        users_used_requests = MessageStatManager.getAllMessagesCount(chatId)

        if subscription is not None:
            return True
        elif users_used_requests < 10:
            return True

        return False
    
    @classmethod
    def rejectPremiumRequest(cls, chatId):
        subscription = cls.getInActivePremiumSubsctiption(
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
    def getNotPaidPremiumSubsctiption(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, isCanceled=False).first()


    @staticmethod
    def getPremiumSubsctiption(
            chatId,
            planId
        ):
            return session.query(Subscription).filter_by(chatId=chatId, planId=planId, isCanceled=False, is_paid=True).first()


    @staticmethod
    def getInActivePremiumSubsctiption(
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
        return session.query(Subscription).filter_by(planId=PlanManager.getPremiumPlanOrCreate().id, isCanceled=False).count()
    
        

class LimitManager:
    
    
    @classmethod
    def checkGptRRequestsDailyLimit(cls, chatId):
        users_plan_limit = cls.getDailyGptLimitOfUser(chatId)
        users_used_requests = MessageStatManager.getTodaysMessage(chatId)
        
        if users_plan_limit > users_used_requests:
            return True
        
        return False
    
    @classmethod
    def checkImageaiRequestsDailyLimit(cls, chatId):
        users_plan_limit = cls.getDailyImageAiLimitOfUser(chatId)
        users_used_requests = MessageStatManager.getTodaysImages(chatId)
        
        if users_plan_limit > users_used_requests:
            return True
        
        return False

    @classmethod
    def dailyLimitOfUser(cls):
        cls.free_plan = PlanManager.getFreePlanOrCreate()
        cls.premium_plan = PlanManager.getPremiumPlanOrCreate()
        
        cls.premium_subscription = session.query(Subscription).filter_by(
            chatId=cls.chatId, planId=cls.premium_plan.id, is_paid=True, isCanceled=False).first()
        
        cls.free_subscription = session.query(Subscription).filter_by(
            chatId=cls.chatId, planId=cls.free_plan.id, is_paid=True, isCanceled=False).first()
        
    
    @classmethod
    def getDailyGptLimitOfUser(
        cls,       
        chatId
    ):
        cls.chatId = chatId
        

        cls.dailyLimitOfUser()

        if cls.premium_subscription is not None:
            return int(cls.premium_plan.monthlyLimitedGptrequests) / 30 # get daily limit requests
        elif cls.free_subscription is not None:
            return int(cls.free_plan.monthlyLimitedGptrequests) / 30
        else:
            SubscriptionManager.createSubscription(
                planId=cls.free_plan.id,
                chatId=chatId,
                cardholder=None,
                is_paid=True,
                isFree=True
            )

            return int(cls.free_plan.monthlyLimitedGptrequests) / 30
        
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
            new_plan = Plan(
                title="Free plan",
                amountForMonth=0,
                monthlyLimitedGptrequests=constants.FREE_GPT_REQUESTS_MONTHLY,
                monthlyLimitedImageRequests=constants.FREE_IMAGEAI_REQUESTS_MONTHLY,
                isFree=True
            )

            session.add(new_plan)
            session.commit()
            
            return new_plan
        
        return plan


    @staticmethod
    def getPremiumPlanOrCreate():
        plan = session.query(Plan).filter_by(isFree=False).first()
        
        if plan is None:
            new_plan = Plan(
                title="Premium plan",
                amountForMonth=constants.PREMIUM_PRICE,
                monthlyLimitedGptrequests=constants.PREMIUM_GPT_REQUESTS_MONTHLY,
                monthlyLimitedImageRequests=constants.PREMIUM_IMAGEAI_REQUESTS_MONTHLY,
                isFree=False
            )

            session.add(new_plan)
            session.commit()
            
            return new_plan
        
        return plan


    @staticmethod
    def getFreePlanUsers():
        free_plan = PlanManager.getFreePlanOrCreate()
        
        free_subscription_users = session.query(Subscription).filter(
            Subscription.planId == free_plan.id, Subscription.is_paid == True, 
            Subscription.isCanceled==False).all()
        
        return free_subscription_users

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
    

