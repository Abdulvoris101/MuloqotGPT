from sqlalchemy import Column, Integer, String, Enum, UnicodeText, Boolean, Text, BigInteger, DateTime, ForeignKey
from db.setup import session, Base
from datetime import datetime
import json
from sqlalchemy.orm import relationship

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chatName = Column(String)
    username = Column(String, nullable=True)
    isActivated = Column(Boolean)
    chatId = Column(BigInteger, unique=True)
    createdAt = Column(DateTime, nullable=True)
    autoTranslate = Column(Boolean, default=False)
    lastUpdated = Column(DateTime, nullable=True)
    
    messageStats = relationship('MessageStats', backref='chat', lazy='dynamic')

    def __init__(self, chatId, chatName, username, isActivated=True):
        self.chatName = chatName
        self.chatId = chatId
        self.username = username
        self.createdAt = datetime.now()
        self.isActivated = isActivated
        super().__init__()

    def save(self):
        session.add(self)
        session.commit()

        return self
    
    @classmethod
    def get(cls, chatId):
        chat = session.query(Chat).filter_by(chatId=chatId).first()

        if chat is not None:
            if chat.autoTranslate is None:
                chat.autoTranslate = False
        
            chat.save()

        return chat

    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(self, chatId):
        chat = session.query(Chat).filter_by(chatId=chatId).first()
        session.delete(chat)


class MessageStats(Base):
    __tablename__ = 'messageStats'

    id = Column(Integer, primary_key=True)
    chatId = Column(BigInteger, ForeignKey('chat.chatId'))
    outputTokens = Column(BigInteger, default=0)
    inputTokens = Column(BigInteger, default=0)
    allMessages = Column(BigInteger, default=0)
    todaysImages = Column(BigInteger, default=0)
    todaysMessages = Column(BigInteger, default=0)


    def __init__(self, chatId):
        self.chatId = chatId


    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(self, chatId):
        messageStat = session.query(Chat).filter_by(chatId=chatId).first()
        session.delete(messageStat)

    @classmethod
    def get(cls, chatId):
        messageStat = session.query(MessageStats).filter_by(chatId=chatId).first()
        return messageStat

    def save(self):
        session.add(self)
        session.commit()


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    
    content = Column(Text)
    role = Column(Enum('user', 'system', 'assistant', name="role_enum", create_type=False))
    uzMessage = Column(Text, nullable=True)
    
    chatId = Column(BigInteger)
    createdAt = Column(DateTime, nullable=True)

    def save(self):
        self.createdAt = datetime.now()
                
        session.add(self)
        session.commit()
        
    @classmethod
    def count(cls):
        messageStats = session.query(MessageStats).all()
        msg_counts = 1

        for messageStat in messageStats:
            messages_count = messageStat.allMessages
            
            if messages_count is not None:
                msg_counts += messages_count

        # Calculate the total count of messages from all chats
        totalMessagesCount = msg_counts

        return totalMessagesCount

    
    @classmethod
    def delete(self, chatId):
        session.query(Message).filter_by(chatId=chatId).delete()

