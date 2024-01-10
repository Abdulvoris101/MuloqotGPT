from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(UUID(as_uuid=True))
    chat_id = Column(BigInteger)
    amount = Column(Integer)
    price = Column(BigInteger)
    is_success = Column(Boolean, default=True)
    cardholder = Column(String, nullable=True)
    created_at = Column(DateTime)

    def __init__(self, transaction_id, chat_id, amount, is_success, cardholder=None):
        self.transaction_id = transaction_id
        self.chat_id = chat_id
        self.amount = amount
        self.created_at = datetime.utcnow()
        self.is_success = is_success
        self.cardholder = cardholder

        super().__init__()

    def save(self):
        session.add(self)
        session.commit()

        return self


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    amount_for_week = Column(BigInteger)
    is_free = Column(Boolean)
    weekly_limited_imagerequests = Column(Integer)
    weekly_limited_gptrequests = Column(Integer)
    subscriptions = relationship('subscription', backref='plan')



    def __init__(
            self, title, description, 
            amount_for_week, is_free, 
            weekly_limited_imagerequests, 
            weekly_limited_gptrequests):
        
        self.title = title
        self.description = description
        self.amount_for_week = amount_for_week
        self.is_free = is_free
        self.weekly_limited_imagerequests = weekly_limited_imagerequests
        self.weekly_limited_gptrequests = weekly_limited_gptrequests
        
        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self
    
    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(self, plan_id):
        chat = session.query(Plan).filter_by(id=plan_id).first()
        session.delete(chat)


class Subscription(Base):
    __tablename__ = 'subscription'
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plan.id'))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    chat_id = Column(BigInteger)
    isCanceled = Column(Boolean, default=False)
    canceledAt = Column(DateTime, nullable=True)


    def __init__(self, plan_id, current_period_start, current_period_end, is_paid, chat_id):
        self.plan_id = plan_id
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.is_paid = is_paid
        self.chat_id = chat_id

        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self
    
    