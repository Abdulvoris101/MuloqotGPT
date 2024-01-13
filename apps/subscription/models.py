from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    amount_for_week = Column(BigInteger)
    is_free = Column(Boolean)
    weekly_limited_imagerequests = Column(Integer)
    weekly_limited_gptrequests = Column(Integer)


    def __init__(
            self, title,
            amount_for_week, is_free, 
            weekly_limited_imagerequests, 
            weekly_limited_gptrequests):
        
        self.id = uuid.uuid4()
        self.title = title
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
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    plan_id = Column(UUID(as_uuid=True))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime, nullable=True)
    is_paid = Column(Boolean, default=False)
    chat_id = Column(BigInteger)
    cardholder = Column(String, nullable=True)
    is_canceled = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)


    def __init__(self, plan_id, cardholder, current_period_start, current_period_end, is_paid, chat_id):
        self.id = uuid.uuid4()
        self.plan_id = plan_id
        self.cardholder = cardholder
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.is_paid = is_paid
        self.chat_id = chat_id

        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self
    
class FreeApiKey(Base):
    __tablename__ = 'freeapikey'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    api_key = Column(String)
    is_used = Column(Boolean, default=False)
    
class Configuration(Base):
    __tablename__ = "configuration"
    
    id = Column(Integer, primary_key=True)
    freeapikey_position = Column(Integer, default=0)
    
    
    def __init__(self, freeapikey_position):
        
        self.freeapikey_position = freeapikey_position

        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self