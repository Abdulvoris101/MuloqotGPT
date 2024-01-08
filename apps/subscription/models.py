from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime, Enum
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
    amount_for_week = Column(BigInteger)
    is_free = Column(Boolean)
    limited_requests = Column(Integer)


    def __init__(self, title, amount_for_week, is_free, limited_requests):
        self.title = title
        self.amount_for_week = amount_for_week
        self.is_free = is_free
        self.limited_requests = limited_requests

        super().__init__()

    def save(self):
        session.add(self)
        session.commit()

        return self

class Subscription(Base):
    id = Column(Integer, primary_key=True)
    planId = Column(Integer)
    currentPeriodStart = Column(DateTime)
    currentPeriodEnd = Column(DateTime)
    paid = Column(Boolean)


