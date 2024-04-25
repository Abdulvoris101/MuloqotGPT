from aiogram import types
from sqlalchemy import Column, Integer, desc, String, Enum, Boolean, Text, BigInteger, DateTime, ForeignKey

from apps.core.schemes import ChatBase
from db.setup import session, Base
from datetime import datetime
from sqlalchemy.orm import relationship, class_mapper


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chatId = Column(BigInteger, unique=True)
    chatName = Column(String)
    chatType = Column(Enum('private', 'group', 'supergroup', name="chat_type_enum"), server_default='private')
    username = Column(String, nullable=True)
    createdAt = Column(DateTime, nullable=True)
    lastUpdated = Column(DateTime, nullable=True)
    chatActivity = relationship('ChatActivity', backref='chat', lazy='dynamic')

    def __init__(self, chatId, chatName, chatType, username, createdAt, lastUpdated):
        self.chatName = chatName
        self.chatId = chatId
        self.chatType = chatType
        self.username = username
        self.createdAt = createdAt
        self.lastUpdated = lastUpdated
        super().__init__()

    def save(self):
        session.add(self)
        session.commit()

        return self
    
    @classmethod
    def get(cls, chatId):
        chat = session.query(Chat).filter_by(chatId=chatId).first()

        return chat

    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(cls, chatId):
        chat = session.query(Chat).filter_by(chatId=chatId).first()
        session.delete(chat)

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}


class ChatActivity(Base):
    __tablename__ = 'chat_activity'

    id = Column(Integer, primary_key=True)
    chatId = Column(BigInteger, ForeignKey('chat.chatId'))
    allMessages = Column(BigInteger, default=0)
    translatedMessagesCount = Column(Integer, default=0)

    def __init__(self, chatId):
        self.chatId = chatId

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}

    @classmethod
    def update(cls, instance, column, value):
        setattr(instance, column, value)
        session.commit()

    @classmethod
    def delete(cls, chatId):
        chatActivity = session.query(Chat).filter_by(chatId=chatId).first()
        session.delete(chatActivity)

    @classmethod
    def get(cls, chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        return chatActivity

    @classmethod
    def getOrCreate(cls, chatId):
        chatActivity = ChatActivity.get(chatId)
        if chatActivity is None:
            ChatActivity(chatId=chatId).save()
            chatActivity = ChatActivity.get(chatId)
        return chatActivity

    def save(self):
        session.add(self)
        session.commit()


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(Text)
    role = Column(Enum('user', 'system', 'assistant', name="role_enum", create_type=False))
    messageType = Column(Enum('message', 'image', name="message_type_enum", create_type=False), default='message')
    uzMessage = Column(Text, nullable=True)
    tokensCount = Column(BigInteger, nullable=True, default=0)
    chatId = Column(BigInteger)
    createdAt = Column(DateTime, nullable=True)

    def __init__(self, chat: dict, role: str, content: str, messageType: str,
                 uzMessage: str, tokensCount: int, createdAt: datetime):
        self.chatId = chat.get("chatId")
        self.role = role
        self.content = content
        self.uzMessage = uzMessage
        self.messageType = messageType
        self.tokensCount = tokensCount
        self.createdAt = createdAt

    def save(self):
        session.add(self)
        session.commit()
    
    @classmethod
    def count(cls) -> int:
        return session.query(Message).order_by(desc(Message.createdAt)).count()


