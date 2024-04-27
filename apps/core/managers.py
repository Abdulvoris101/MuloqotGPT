from typing import List

from .models import Chat, Message, ChatActivity
from utils import countTokenOfMessage
from apps.admin.events import sendEvent
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, func, desc, and_, distinct, Date, exists
from datetime import datetime, timedelta, date
from aiogram import types
from utils import text
from .schemes import ChatCreateScheme, MessageCreateScheme, ChatBase


class ChatManager:

    @classmethod
    def groupsCount(cls) -> int:
        return session.query(Chat).filter_by(chatType='supergroup').count()

    @classmethod
    def usersCount(cls) -> int:
        return session.query(Chat).filter_by(chatType='private').count()

    @classmethod
    def all(cls) -> List[Chat]:
        return session.query(Chat).all()

    @classmethod
    def isExistsByUserId(cls, chatId: int) -> bool:
        return session.query(exists().where(Chat.chatId == chatId)).scalar()

    @classmethod
    async def register(cls, chat: types.Chat) -> None:
        chatData = chat.model_dump()
        chatData["full_name"] = chat.full_name
        scheme = ChatCreateScheme(**chatData)
        scheme.chatType = scheme.chatType.value
        chatObj = Chat(**scheme.model_dump())
        chatObj.save()

        if not MessageManager.isSystemMessagesExist(chatId=chat.id):
            MessageProcessor.createSystemMessages(chat)

        await sendEvent(text=text.USER_REGISTERED_EVENT_TEMPLATE.format_map(chatObj.to_dict()))

    @classmethod
    def updateChatLastVisit(cls, chatId: int):
        chat = Chat.get(chatId=chatId)
        chat.lastUpdated = datetime.now()

# Analytics


class ChatActivityManager:

    @staticmethod
    def incrementActivityCount(chatId: int, column: str) -> None:
        chatActivity = ChatActivity.get(chatId=chatId)
        currentValue = getattr(chatActivity, column)

        ChatActivity.update(chatActivity, column, currentValue + 1)

    @classmethod
    def getCurrentMonthUsers(cls) -> int:
        thirtyDaysAgo = datetime.now() - timedelta(days=30)

        return session.query(Chat).filter(
            Chat.lastUpdated >= thirtyDaysAgo
        ).count()

    @classmethod
    def getUserActivityTimeFrame(cls, days=1) -> int:
        timeThreshold = datetime.now() - timedelta(days=days)
        return session.query(Chat).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) >= timeThreshold
        ).count()

    @classmethod
    def getActiveUsersTimeFrame(cls, days=1) -> int:
        activeChatsCount = session.query(Chat.chatId).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) - Chat.createdAt >= timedelta(days=days)
        ).distinct().count()
        return activeChatsCount

    @classmethod
    def getLatestChat(cls) -> Chat:
        return session.query(Chat).\
            filter(Chat.lastUpdated.isnot(None)).\
            order_by(desc(Chat.lastUpdated)).first()


class MessageManager:

    @classmethod
    def getLimitedMessages(cls, chatId: int, maxTokens: int) -> List[dict]:
        """Retrieve all messages for a given chat ID up to a maximum number of tokens,
        return them as a list of dictionaries."""
        messages = session.query(Message).filter_by(chatId=chatId, messageType="message", isCleaned=False).order_by(
            Message.id.desc()).limit(100).all()

        systemMessages = session.query(Message).filter_by(chatId=chatId, messageType="message",
                                                          role='system').all()
        messages = systemMessages + messages

        includedMessages = []
        currentTokens = 0

        for message in messages:
            if currentTokens + message.tokensCount > maxTokens:
                break

            includedMessages.append({
                "content": message.content,
                "role": message.role,
            })
            currentTokens += message.tokensCount

        return includedMessages[::-1]

    @classmethod
    def saveMessage(cls, messageScheme: MessageCreateScheme):
        """Save a message based on a dictionary of message data."""
        obj = Message(**messageScheme.model_dump())
        obj.save()

    @classmethod
    def addMessage(cls, content: str, uzMessage: str, chat: types.Chat,
                   role: str) -> None:
        tokensCount = countTokenOfMessage(content)
        chatData = chat.model_dump(by_alias=True)
        chatData["full_name"] = chat.full_name

        messageScheme = MessageCreateScheme(content=content, role=role, messageType='message',
                                            uzMessage=uzMessage, tokensCount=tokensCount,
                                            chat=ChatBase(**chatData))
        messageScheme.role = messageScheme.role.value
        messageScheme.messageType = messageScheme.messageType.value
        cls.saveMessage(messageScheme)

    @classmethod
    def addImage(cls, query: str, chat: types.Chat) -> None:
        chatData = chat.model_dump(by_alias=True)
        chatData["full_name"] = chat.full_name

        messageScheme = MessageCreateScheme(content=query, role='user', messageType='image',
                                            uzMessage="", tokensCount=0, chat=ChatBase(**chatData))
        messageScheme.role = messageScheme.role.value
        messageScheme.messageType = messageScheme.messageType.value
        cls.saveMessage(messageScheme)

    @classmethod
    def getMessagesActivityTimeFrame(cls, days: int = 1, messageType: str = "message") -> int:
        timeThreshold = datetime.now() - timedelta(days=days)

        return session.query(Message).filter(
            and_(Message.createdAt >= timeThreshold,
                 Message.messageType == messageType,
                 Message.role == 'user')
        ).count()

    @classmethod
    def getUserMessagesTimeFrame(cls, chatId: int, days: int = 1, messageType: str = "message") -> int:
        timeThreshold = datetime.now() - timedelta(days=days)

        return session.query(Message).filter(
            and_(Message.createdAt >= timeThreshold,
                 Message.messageType == messageType,
                 Message.chatId == chatId,
                 Message.role == 'user')
        ).count()

    @classmethod
    def countTokens(cls, role: str) -> int:
        totalTokens = session.query(func.sum(Message.tokensCount)) \
                           .filter(
            Message.role == role,
            Message.messageType == 'message'
        ).scalar()

        return totalTokens

    @classmethod
    def isSystemMessagesExist(cls, chatId: int):
        return session.query(Message).filter_by(chatId=chatId, role='system').count() >= 1

    @classmethod
    def clearUserChat(cls, chatId: int):
        messages = session.query(Message).filter_by(chatId=chatId, isCleaned=False).all()

        for message in messages:
            message.isCleaned = True
            session.add(message)

        session.commit()
