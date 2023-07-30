from db.setup import Base, session
from sqlalchemy import Column, Integer, String, UUID, BigInteger, Boolean, DateTime
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