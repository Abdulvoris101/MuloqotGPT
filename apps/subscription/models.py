from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime, ForeignKey
import uuid


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    amountForMonth = Column(BigInteger)
    isFree = Column(Boolean)
    monthlyLimitedImageRequests = Column(Integer)
    monthlyLimitedGptRequests = Column(Integer)
    isGroup = Column(Boolean)
    isHostGroup = Column(Boolean)

    def __init__(
            self, title,
            amountForMonth, isFree, 
            monthlyLimitedImageRequests, 
            monthlyLimitedGptRequests, isGroup, isHostGroup):
        
        self.id = uuid.uuid4()
        self.title = title
        self.amountForMonth = amountForMonth
        self.isFree = isFree
        self.monthlyLimitedImageRequests = monthlyLimitedImageRequests
        self.monthlyLimitedGptRequests = monthlyLimitedGptRequests
        self.isGroup = isGroup
        self.isHostGroup = isHostGroup
        
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
    def delete(cls, planId):
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

    def __init__(self, planId,
                 cardholder, currentPeriodStart,
                 currentPeriodEnd, is_paid, chatId):

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


class ChatQuota(Base):
    __tablename__ = 'chat_quota'

    id = Column(Integer, primary_key=True)
    chatId = Column(BigInteger, ForeignKey('chat.chatId'))
    additionalGptRequests = Column(BigInteger, default=0)
    additionalImageRequests = Column(BigInteger, default=0)

    def __init__(self, chatId, additionalGptRequests=0, additionalImageRequests=0):
        self.chatId = chatId
        self.additionalGptRequests = additionalGptRequests
        self.additionalImageRequests = additionalImageRequests

    def save(self):
        session.add(self)
        session.commit()

    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(cls, chatId):
        chatQuota = cls.get(chatId)
        session.delete(chatQuota)

    @classmethod
    def get(cls, chatId):
        chatQuota = session.query(ChatQuota).filter_by(chatId=chatId).first()
        return chatQuota

    @classmethod
    def getOrCreate(cls, chatId):
        chatQuota = cls.get(chatId)

        if chatQuota is None:
            ChatQuota(
                chatId=chatId, additionalGptRequests=0,
                additionalImageRequests=0).save()

        return cls.get(chatId)



