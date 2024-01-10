from .models import Subscription, Plan
import datetime
from db.setup import session
from utils import text

class SubscriptionManager:
    
    @staticmethod
    def subscribe(
        plan_id,
        chat_id
    ):
        subscription = Subscription(
            plan_id=plan_id,
            current_period_start=datetime.datetime.now(),
            current_period_end=datetime.datetime.now() + datetime.timedelta(days=7),
            is_paid=True,
            chat_id=chat_id
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
    def getFreePlanOrCreate():
        plan = session.query(Plan).filter_by(is_free=True)
        
        if plan is None:
            new_plan = Plan(
                title="Free plan",
                description=text.FREE_GPT_PLAN_TEXT,
                amount_for_week=0,
                weekly_limited_gptrequests=140,
                weekly_limited_imagerequests=35,
                is_free=True
            )

            new_plan.save()

        

                