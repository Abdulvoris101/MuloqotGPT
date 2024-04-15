from typing import List

from .models import Chat, Message, ChatActivity
from utils import countTokenOfMessage, constants
from utils.translate import skipCodeTranslation
from utils.events import sendEvent
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, func, desc, and_, distinct, Date, exists, select
from datetime import datetime, timedelta, date
from aiogram import types
from utils import text
from .schemes import ChatCreateScheme, MessageCreateScheme


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
    def isExistsByUserId(cls, userId: int) -> bool:
        return session.query(exists().where(Chat.chatId == userId)).scalar()

    @classmethod
    async def register(cls, chat: types.Chat) -> None:
        scheme = ChatCreateScheme(**chat.model_dump(by_alias=True))
        scheme.chatType = scheme.chatType.value

        chatObj = Chat(**scheme.model_dump())
        chatObj.save()

        MessageProcessor.createSystemMessages(chat)

        await sendEvent(text=text.getUserRegisterEventText(chat=chatObj))


# Analytics


class ChatActivityManager:

    @classmethod
    def countTokens(cls, columnName: str, today=False) -> int:
        column = getattr(ChatActivity, columnName, None)

        if column is None:
            raise ValueError(f"Invalid column name: {columnName}")

        query = session.query(
            func.sum(column).label(columnName),
        )

        if today:
            query = query.filter(ChatActivity.todaysMessages >= 1)

        result = query.one()

        return getattr(result, columnName) or 0

    @staticmethod
    def resetTodayCounters() -> None:
        session.query(ChatActivity).update({
            ChatActivity.todaysMessages: 0,
            ChatActivity.todaysImages: 0
        })
        session.commit()

    @staticmethod
    def incrementActivityCount(chatId: int, column: str) -> None:
        chatActivity = ChatActivity.get(chatId=chatId)
        currentValue = getattr(chatActivity, column)
        ChatActivity.update(chatActivity, column, currentValue + 1)

    @classmethod
    def updateTokenCount(cls, chatId: int, columnName: str, message: str):
        activity = ChatActivity.get(chatId=chatId)
        tokenCount = countTokenOfMessage(message)
        currentTokens = getattr(activity, columnName, 0) or 0
        setattr(activity, columnName, currentTokens + tokenCount)
        session.commit()

    @classmethod
    def getLimitReachedUsers(cls) -> int:
        return session.query(ChatActivity).filter_by(todaysMessages=16).count()

    @classmethod
    def getCurrentMonthUsers(cls) -> int:
        thirtyDaysAgo = datetime.now() - timedelta(days=30)

        return session.query(Chat).filter(
            Chat.lastUpdated >= thirtyDaysAgo
        ).count()

    @classmethod
    def getTodayActiveUsers(cls) -> int:
        return session.query(ChatActivity.todaysMessages).filter(
            ChatActivity.todaysMessages >= 1
        ).count()

    @classmethod
    def getUserActivityTimeFrame(cls, days=1) -> int:
        timeThreshold = datetime.now() - timedelta(days=days)
        return session.query(ChatActivity).filter(
            func.coalesce(ChatActivity.lastUpdated, ChatActivity.createdAt) >= timeThreshold
        ).count()

    @classmethod
    def getLatestChat(cls) -> Chat:
        return session.query(Chat).\
            filter(Chat.lastUpdated.isnot(None)).\
            order_by(desc(Chat.lastUpdated)).first()


class MessageManager:

    @classmethod
    def all(cls, chatId) -> List[dict]:
        """Retrieve all messages for a given chat ID and return them as a list of dictionaries."""
        messages = session.query(Message).filter_by(chatId=chatId).order_by(Message.id).all()
        return [{"content": message.content, "role": message.role} for message in messages]

    @classmethod
    def saveMessage(cls, messageScheme: MessageCreateScheme):
        """Save a message based on a dictionary of message data."""
        obj = Message(**messageScheme.model_dump())
        obj.save()

    @classmethod
    def userRole(cls, translatedText, instance: types.Message) -> None:
        messageScheme = MessageCreateScheme(content=translatedText, role='user',
                                            uzMessage=instance.text, **instance.model_dump())
        messageScheme.role = messageScheme.role.value
        cls.saveMessage(messageScheme)

        ChatActivityManager.updateTokenCount(chatId=instance.chat.id, columnName='inputTokens',
                                             message=translatedText)

    @classmethod
    def assistantRole(cls, originalText: str, uzMessage: str, instance: types.Message) -> None:
        messageScheme = MessageCreateScheme(content=originalText, role='assistant',
                                            uzMessage=uzMessage, **instance.model_dump())
        messageScheme.role = messageScheme.role.value
        cls.saveMessage(messageScheme=messageScheme)

    @classmethod
    def systemRole(cls, instance: types.Message) -> None:
        messageScheme = MessageCreateScheme(role='system', content=instance.text, uzMessage='',
                                            **instance.model_dump())
        messageScheme.role = messageScheme.role.value
        cls.saveMessage(messageScheme=messageScheme)

    @classmethod
    def systemToAllChat(cls, text: str) -> None:
        chats = ChatManager.all()

        for chat in chats:
            messageScheme = MessageCreateScheme(chat=chat, role='system', content=text,
                                                uzMessage=None)
            cls.saveMessage(messageScheme)

    @classmethod
    def deleteByLimit(cls, chatId: int):
        """Delete messages by a specific retention limit, excluding the latest system message."""
        messagesToKeep = session.query(Message.id).filter(
            Message.chatId == chatId, Message.role == "system"
        ).order_by(Message.id.desc()).limit(1).subquery()

        # Convert subquery to a select() explicitly for use in notin_()
        messages_to_keep_select = select([messagesToKeep.c.id])

        # Delete all other messages that are not in the list of messages to keep
        messages_to_delete = session.query(Message).filter(
            Message.chatId == chatId,
            Message.id.notin_(messages_to_keep_select)
        ).delete(synchronize_session=False)

        session.commit()

    @classmethod
    def getSystemMessages(cls) -> List[dict]:
        chat = session.query(Chat).order_by(desc(Chat.id)).first()

        messages = session.query(Message).filter_by(chatId=chat.chatId).all()
        listed_messages = []

        for message in messages:
            data = {"content": message.content, "role": message.role}

            if data["role"] == "system":
                listed_messages.append(data)

        return listed_messages

    @classmethod
    def getTodayMessagesCount(cls) -> int:
        return session.query(func.count(Message.id)). \
                filter(cast(Message.createdAt, Date) == date.today()).scalar()

