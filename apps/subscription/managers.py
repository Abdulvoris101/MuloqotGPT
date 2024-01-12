from .models import Subscription, Plan
import datetime
from db.setup import session
from utils import text
from utils import constants

class SubscriptionManager:
    
    @classmethod
    def subscribe(
        cls,
        plan_id,
        chat_id,
        cardholder=None,
        is_paid=False,
        is_free=True
    ):
        
        if is_free:
            free_inactive_subscription = cls.getUserFreeInactiveSubscription(chat_id)
                
            if free_inactive_subscription is not None:    
                free_inactive_subscription.is_paid = True
                free_inactive_subscription.is_canceled = True
                
                session.add(free_inactive_subscription) # set active the free subscription
                session.commit()
            
        
        subscription = Subscription(
            plan_id=plan_id,
            current_period_start=datetime.datetime.now(),
            current_period_end=datetime.datetime.now() + datetime.timedelta(days=7),
            is_paid=is_paid,
            chat_id=chat_id,
            cardholder=cardholder
        )
        
        if is_free:
            subscription.current_period_end = None
        
        session.add(subscription)
        session.commit()
        
        return subscription
    
    
    @classmethod
    def getUserFreeInactiveSubscription(cls, chat_id):
        free_inactive_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=PlanManager.getFreePlanOrCreate().id, is_paid=False, is_canceled=True).first()
        
        
        return free_inactive_subscription
    
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
        
    @staticmethod
    def findByChatIdAndPlanId(
        chat_id,
        plan_id
    ):
        return session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id, is_paid=True, is_canceled=False).first()

    
    @staticmethod
    def getByChatId(
        chat_id
    ):
        return session.query(Subscription).filter_by(chat_id=chat_id).first()
        
    @classmethod
    def getDailyGptLimitOfUser(
        cls,       
        chat_id
    ):
        free_plan = PlanManager.getFreePlanOrCreate()
        premium_plan = PlanManager.getPremiumPlanOrCreate()
        
        premium_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=premium_plan.id, is_paid=True, is_canceled=False).first()
        
        free_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=free_plan.id, is_paid=True, is_canceled=False).first()
        
        
        if premium_subscription is not None:
            return int(premium_plan.weekly_limited_gptrequests) / 7 # get daily limit requests
        elif free_subscription is not None:
            
            return int(free_plan.weekly_limited_gptrequests) / 7
        else:
            
            free_inactive_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=free_plan.id, is_paid=False, is_canceled=True).first()
            
            if free_inactive_subscription is not None:    
                free_inactive_subscription.is_paid = True
                free_inactive_subscription.is_canceled = True
                
                session.add(free_inactive_subscription) # set active the free subscription
                session.commit()
                
            else: 
                cls.subscribe(
                    plan_id=free_plan.id,
                    chat_id=chat_id,
                    cardholder=None,
                    is_paid=True,
                    is_free=True
                )

                
            return int(free_plan.weekly_limited_gptrequests) / 7
        
    @classmethod
    def getDailyImageAiLimitOfUser(
        cls,       
        chat_id
    ):
        free_plan = PlanManager.getFreePlanOrCreate()
        premium_plan = PlanManager.getPremiumPlanOrCreate()
        
        premium_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=premium_plan.id, is_paid=True).first()
        
        free_subscription = session.query(Subscription).filter_by(
            chat_id=chat_id, plan_id=free_plan.id, is_paid=True).first()
        
        
        if premium_subscription is not None:
            return int(premium_plan.weekly_limited_imagerequests) / 7 # get daily limit requests
        elif free_subscription is not None:
            return int(free_plan.weekly_limited_imagerequests) / 7
        else:
            # create free subscription for user
            cls.subscribe(
                free_plan.id,
                chat_id
            )
            
            return int(free_plan.weekly_limited_imagerequests) / 7
            
            
    

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


    

                