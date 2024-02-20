from sqlalchemy import Column, Integer, desc, String, Enum, Boolean, Text, BigInteger, DateTime, ForeignKey
from db.setup import session, Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chatName = Column(String)
    username = Column(String, nullable=True)
    chatId = Column(BigInteger, unique=True)
    createdAt = Column(DateTime, nullable=True)
    lastUpdated = Column(DateTime, nullable=True)
    
    chatActivity = relationship('ChatActivity', backref='chat', lazy='dynamic')

    def __init__(self, chatId, chatName, username):
        self.chatName = chatName
        self.chatId = chatId
        self.username = username
        self.createdAt = datetime.now()
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


class ChatActivity(Base):
    __tablename__ = 'chat_activity'

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
    def delete(cls, chatId):
        chatActivity = session.query(Chat).filter_by(chatId=chatId).first()
        session.delete(chatActivity)

    @classmethod
    def get(cls, chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        return chatActivity

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
        last_message = session.query(Message).order_by(desc(Message.createdAt)).first()

        return int(last_message.id)
    
    @classmethod
    def delete(cls, chatId):
        session.query(Message).filter_by(chatId=chatId).delete()

