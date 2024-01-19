from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    amountForMonth = Column(BigInteger)
    isFree = Column(Boolean)
    monthlyLimitedImageRequests = Column(Integer)
    monthlyLimitedGptrequests = Column(Integer)


    def __init__(
            self, title,
            amountForMonth, isFree, 
            monthlyLimitedImageRequests, 
            monthlyLimitedGptrequests):
        
        self.id = uuid.uuid4()
        self.title = title
        self.amountForMonth = amountForMonth
        self.isFree = isFree
        self.monthlyLimitedImageRequests = monthlyLimitedImageRequests
        self.monthlyLimitedGptrequests = monthlyLimitedGptrequests
        
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
    def delete(self, planId):
        chat = session.query(Plan).filter_by(id=planId).first()
        session.delete(chat)
        



class Subscription(Base):
    __tablename__ = 'subscription'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    planId = Column(UUID(as_uuid=True))
    currentPeriodStart = Column(DateTime)
    currentPeriodEnd = Column(DateTime, nullable=True)
    is_paid = Column(Boolean, default=False)
    chatId = Column(BigInteger)
    cardholder = Column(String, nullable=True)
    isCanceled = Column(Boolean, default=False)
    canceledAt = Column(DateTime, nullable=True)


    def __init__(self, planId, cardholder, currentPeriodStart, currentPeriodEnd, is_paid, chatId):
        self.id = uuid.uuid4()
        self.planId = planId
        self.cardholder = cardholder
        self.currentPeriodStart = currentPeriodStart
        self.currentPeriodEnd = currentPeriodEnd
        self.is_paid = is_paid
        self.chatId = chatId

        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self
    
class FreeApiKey(Base):
    __tablename__ = 'freeapikey'
    
    id = Column(Integer, primary_key=True)
    apiKey = Column(String)
    isExpired = Column(Boolean, default=False)
    requests = Column(Integer, default=1)
    

class Configuration(Base):
    __tablename__ = "configuration"
    
    id = Column(Integer, primary_key=True)
    apikeyPosition = Column(Integer, default=0)
    
    
    def __init__(self, apikeyPosition):
        
        self.apikeyPosition = apikeyPosition

        super().__init__()


    def save(self):
        session.add(self)
        session.commit()

        return self
    

