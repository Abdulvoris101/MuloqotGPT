from .models import Subscription, Plan
import datetime
from db.setup import session
from utils import text
from utils import constants
import uuid

class SubscriptionManager:
    
    @staticmethod
    def subscribe(
        plan_id,
        chat_id,
        cardholder=None
    ):
        subscription = Subscription(
            plan_id=plan_id,
            subscription_id=uuid.uuid4(),
            current_period_start=datetime.datetime.now(),
            current_period_end=datetime.datetime.now() + datetime.timedelta(days=7),
            is_paid=True,
            chat_id=chat_id,
            cardholder=cardholder
        )
        
        session.add(subscription)
        session.commit()
    
    
    @staticmethod
    def unsubscribe(
        plan_id,
        chat_id
    ):
        subscription = session.query(Subscription).filter_by(chat_id=chat_id, plan_id=plan_id).first()

        if subscription is None:
            return False
        
        subscription.canceledAt = datetime.datetime.now()
        subscription.is_paid = False
        subscription.isCanceled = True
        
        session.add(subscription)
        session.commit()
        
    
    @staticmethod
    def getByChatId(
        chat_id
    ):
        return session.query(Subscription).filter_by(chat_id=chat_id).first()
        

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
                plan_id=uuid.uuid4(),
                amount_for_week=0,
                weekly_limited_gptrequests=constants.FREE_GPT_REQUESTS_WEEKLY,
                weekly_limited_imagerequests=constants.FREE_IMAGEAI_REQUESTS_WEEKLY,
                is_free=True
            )

            new_plan.save()
            
            return new_plan.plan_id
        
        return plan.plan_id


    @staticmethod
    def getPremiumPlanOrCreate():
        plan = session.query(Plan).filter_by(is_free=False).first()
        
        if plan is None:
            new_plan = Plan(
                title="Premium plan",
                plan_id=uuid.uuid4(),
                amount_for_week=constants.PREMIUM_PRICE,
                weekly_limited_gptrequests=constants.PREMIUM_GPT_REQUESTS_WEEKLY,
                weekly_limited_imagerequests=constants.PREMIUM_IMAGEAI_REQUESTS_WEEKLY,
                is_free=True
            )

            new_plan.save()
            
            return new_plan.plan_id
        
        return plan.plan_id


    

                