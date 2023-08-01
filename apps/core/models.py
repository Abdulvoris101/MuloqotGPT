from sqlalchemy import Column, Integer, String, UnicodeText, Boolean, BigInteger, DateTime
from db.setup import session, Base
from datetime import datetime

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    username = Column(String, nullable=True)
    is_activated = Column(Boolean)
    chat_id = Column(BigInteger)
    created_at = Column(DateTime, nullable=True)
    credit = Column(BigInteger, default=100)
    auto_translate = Column(Boolean, default=True)
    last_updated = Column(DateTime, nullable=True)
    messages_count = Column(BigInteger, default=0)

    def __init__(self, chat_id, chat_name, username, is_activated=True):
        self.chat_name = chat_name
        self.chat_id = chat_id
        self.username = username
        self.created_at = datetime.now()
        self.is_activated = is_activated
        super().__init__()

    def save(self):
        session.add(self)
        session.commit()

        return self
    
    @classmethod
    def get(cls, chat_id):
        chat = session.query(Chat).filter_by(chat_id=chat_id).first()

        if chat is not None:
            if chat.auto_translate is None:
                chat.auto_translate = True
            if chat.messages_count is None:
                chat.messages_count = 0
            if chat.credit is None:
                chat.credit = 100
        
            chat.save()

        return chat

    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(self, chat_id):
        chat = session.query(Chat).filter_by(chat_id=chat_id).first()
        session.delete(chat)

    



import json


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    data = Column(UnicodeText)
    chat_id = Column(BigInteger)
    created_at = Column(DateTime, nullable=True)

    def save(self):
        self.created_at = datetime.now()
        self.data = json.dumps(self.data, ensure_ascii=False)
        session.add(self)
        session.commit()
        
    @classmethod
    def count(cls):
        chats = session.query(Chat).all()
        msg_counts = 1

        for chat in chats:
            messages_count = chat.messages_count
            
            if messages_count is not None:
                msg_counts += messages_count

        # Calculate the total count of messages from all chats
        total_messages_count = msg_counts

        return total_messages_count

    
    @classmethod
    def delete(self, chat_id):
        session.query(Message).filter_by(chat_id=chat_id).delete()


# Base.metadata.create_all(engine)

# # Commit the changes and close the session
# session.commit()