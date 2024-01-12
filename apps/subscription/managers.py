from .models import Subscription, Plan
import datetime
from db.setup import session
from utils import text
from utils import constants
from apps.core.managers import MessageStatManager
from sqlalchemy import not_

class SubscriptionManager:
    

    @staticmethod
    def check_gpt_requests_daily_limit(chat_id):
        users_plan_limit = SubscriptionManager.getDailyGptLimitOfUser(chat_id)
        users_used_requests = MessageStatManager.get_todays_message(chat_id)
        
        if users_plan_limit > users_used_requests:
            return True
        
        return False
    
    @staticmethod
    def check_imageai_requests_daily_limit(chat_id):
        users_plan_limit = SubscriptionManager.getDailyImageAiLimitOfUser(chat_id)
        users_used_requests = MessageStatManager.get_todays_images(chat_id)
        
        if users_plan_limit > users_used_requests:
            return True
        
        return False


    @classmethod
    def create_subscription(
        cls,
        plan_id,
        chat_id,
        cardholder=None,
        is_paid=False,
        is_free=True
    ):
        
        if is_free:
            is_activated = cls.reactivateFreeSubscription(chat_id)

            if is_activated:
                return
        
        
        current_period_end = datetime.datetime.now() + datetime.timedelta(days=7)

        subscription = Subscription(
            plan_id=plan_id,
            current_period_start=datetime.datetime.now(),
            current_period_end=None if is_free else current_period_end,
            is_paid=is_paid,
            chat_id=chat_id,
            cardholder=cardholder
        )
        
        session.add(subscription)
        session.commit()
        
        return subscription
    

    @staticmethod
    def unsubscribe(
        plan_id,
        chat_id
    ):
        subscription = session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id).first()

        if subscription is None:
            return False
        
        subscription.canceled_at = datetime.datetime.now()
        subscription.is_paid = False
        subscription.is_canceled = True
        
        session.add(subscription)
        session.commit()
        
        return True
    
    @classmethod
    def subscribe(
        cls,
        plan_id,
        chat_id
    ):
        subscription = cls.getInActivePremiumSubsctiption(
            chat_id=chat_id,
            plan_id=plan_id
        )
        
        
        subscription.is_canceled = False
        subscription.is_paid = True
        
        session.add(subscription)
        session.commit()
    
    @classmethod
    def reactivateFreeSubscription(cls, chat_id):
        inactive_subscription = cls.getUsersFreeInactiveSubscription(chat_id)

        if inactive_subscription is not None:
            inactive_subscription.is_paid = True
            inactive_subscription.is_canceled = False
            inactive_subscription.canceled_at = None

            session.add(inactive_subscription) # set active the free subscription
            session.commit()

            return True
        
        return False
    
    @classmethod
    def isPremiumToken(cls, chat_id):
        subscription = cls.findByChatIdAndPlanId(chat_id=chat_id, 
                                  plan_id=PlanManager.getPremiumPlanOrCreate().id)
        users_used_requests = MessageStatManager.get_all_messages_count(chat_id)

        if subscription is not None:
            return True
        elif users_used_requests < 10:
            return True

        return False
        

    @classmethod
    def getUsersFreeInactiveSubscription(cls, chat_id):
        return session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=PlanManager.getFreePlanOrCreate().id, is_paid=False, is_canceled=True).first()
        
    
        
    @staticmethod
    def findByChatIdAndPlanId(
        chat_id,
        plan_id
    ):
        return session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id).first()


    @staticmethod
    def getNotPaidPremiumSubsctiption(
            chat_id,
            plan_id
        ):
            return session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id, is_canceled=False).first()


    @staticmethod
    def getPremiumSubsctiption(
            chat_id,
            plan_id
        ):
            return session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id, is_canceled=False, is_paid=True).first()


    @staticmethod
    def getInActivePremiumSubsctiption(
            chat_id,
            plan_id
        ):
            return session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id, is_paid=False, is_canceled=False).first()

    
    @staticmethod
    def getByChatId(
        chat_id
    ):
        return session.query(Subscription).filter_by(chat_id=chat_id).first()


    @classmethod
    def dailyLimitOfUser(cls):
        cls.free_plan = PlanManager.getFreePlanOrCreate()
        cls.premium_plan = PlanManager.getPremiumPlanOrCreate()
        
        cls.premium_subscription = session.query(Subscription).filter_by(
            chat_id=cls.chat_id, plan_id=cls.premium_plan.id, is_paid=True, is_canceled=False).first()
        
        cls.free_subscription = session.query(Subscription).filter_by(
            chat_id=cls.chat_id, plan_id=cls.free_plan.id, is_paid=True, is_canceled=False).first()
        
    
    @classmethod
    def getDailyGptLimitOfUser(
        cls,       
        chat_id
    ):
        cls.chat_id = chat_id
        

        cls.dailyLimitOfUser()

        if cls.premium_subscription is not None:
            return int(cls.premium_plan.weekly_limited_gptrequests) / 7 # get daily limit requests
        elif cls.free_subscription is not None:
            return int(cls.free_plan.weekly_limited_gptrequests) / 7
        else:
            cls.create_subscription(
                plan_id=cls.free_plan.id,
                chat_id=chat_id,
                cardholder=None,
                is_paid=True,
                is_free=True
            )

            return int(cls.free_plan.weekly_limited_gptrequests) / 7
        
    @classmethod
    def getDailyImageAiLimitOfUser(
        cls,       
        chat_id
    ):
        cls.chat_id = chat_id

        cls.dailyLimitOfUser()
        
        if cls.premium_subscription is not None:
            return int(cls.premium_plan.weekly_limited_imagerequests) / 7 # get daily limit requests
        elif cls.free_subscription is not None:
            return int(cls.free_plan.weekly_limited_imagerequests) / 7
        else:
            cls.create_subscription(
                plan_id=cls.free_plan.id,
                chat_id=chat_id,
                cardholder=None,
                is_paid=True,
                is_free=True
            )

            return int(cls.free_plan.weekly_limited_imagerequests) / 7

            
    @staticmethod
    def getFreePlanUsers():
        free_plan = PlanManager.getFreePlanOrCreate()
        
        free_subscription_users = session.query(Subscription).filter(
            Subscription.plan_id == free_plan.id, Subscription.is_paid == True, 
            Subscription.is_canceled==False).all()
        
        return free_subscription_users
        

    

class PlanManager:
    
    
    @staticmethod
    def get(plan_id):
        return session.query(Plan).filter_by(id=plan_id)

    
    @staticmethod
    def getFreePlanOrCreate():
        plan = session.query(Plan).filter_by(is_free=True).first()
        
        if plan is None:
            new_plan = Plan(
                title="Free plan",
                amount_for_week=0,
                weekly_limited_gptrequests=constants.FREE_GPT_REQUESTS_WEEKLY,
                weekly_limited_imagerequests=constants.FREE_IMAGEAI_REQUESTS_WEEKLY,
                is_free=True
            )

            session.add(new_plan)
            session.commit()
            
            return new_plan
        
        return plan


    @staticmethod
    def getPremiumPlanOrCreate():
        plan = session.query(Plan).filter_by(is_free=False).first()
        
        if plan is None:
            new_plan = Plan(
                title="Premium plan",
                amount_for_week=constants.PREMIUM_PRICE,
                weekly_limited_gptrequests=constants.PREMIUM_GPT_REQUESTS_WEEKLY,
                weekly_limited_imagerequests=constants.PREMIUM_IMAGEAI_REQUESTS_WEEKLY,
                is_free=False
            )

            session.add(new_plan)
            session.commit()
            
            return new_plan
        
        return plan


    

                