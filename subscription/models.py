from sqlalchemy import Column, select, Integer, String, ForeignKey, BigInteger, JSON, DateTime
from db.setup import session, engine, Base
from datetime import datetime, timedelta
from core.models import Chat


class Limit(Base):
    __tablename__ = 'limit'

    id = Column(Integer, primary_key=True)
    image = Column(BigInteger)


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    amount = Column(BigInteger)
    limit = Column(Integer, ForeignKey('limit.id'))
    createdAt = Column(DateTime, nullable=True)


class Subscription(Base):
    __tablename__ = 'subscription'

    plan = Column(Integer, ForeignKey('plan.id'))
    chat = Column(Integer, ForeignKey('chat.id'))
    
