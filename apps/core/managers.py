from .models import Chat, Message, ChatActivity
from utils import countTokenOfMessage, constants
from utils.translate import skipCodeTranslation
from utils.events import sendEvent
from filters.permission import isGroupAllowed
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, String, func, desc, and_, distinct, Date, exists
from datetime import datetime, timedelta, date
from apps.subscription.models import ChatQuota
from aiogram import types
from utils import text


class ChatManager:

    @classmethod
    def groupsCount(cls):
        return session.query(Chat).filter_by(chatType='supergroup').count()

    @classmethod
    def usersCount(cls):
        return session.query(Chat).filter_by(chatType='private').count()

    @classmethod
    def all(cls):
        return session.query(Chat).all()

    @classmethod
    def isExistsByUserId(cls, userId: int):
        return session.query(exists().where(Chat.chatId == userId)).scalar()

    @classmethod
    async def register(cls, chat: types.Chat):
        chatObj = cls.isExistsByUserId(chat.id)

        if not chatObj:
            Chat(chatId=chat.id, chatName=chat.full_name, chatType=chat.type,
                 username=chat.username).save()
            MessageProcessor.createSystemMessages(chat.id, chat.type)

            await sendEvent(text=text.getUserRegisterEventText(chat=chat))

        ChatActivity.getOrCreate(chat.id)
        ChatQuota.getOrCreate(chat.id)

        session.commit()


# Analytics


class ChatActivityManager:

    @classmethod
    def countOfTodayOutputTokens(cls):
        chats = session.query(ChatActivity).filter(ChatActivity.todaysMessages >= 1)
        outputTokens = 1

        for activity in chats:
            if activity.outputTokens is not None:
                outputTokens += activity.outputTokens

        return outputTokens

    @classmethod
    def countOfTodayInputTokens(cls):
        chats = session.query(ChatActivity).filter(ChatActivity.todaysMessages >= 1)
        inputTokens = 1

        for chat in chats:
            if chat.inputTokens is not None:
                inputTokens += chat.inputTokens

        return inputTokens

    @classmethod
    def countOfAllOutputTokens(cls):
        userActivities = session.query(ChatActivity).all()
        outputTokens = 1

        for activity in userActivities:
            if activity.outputTokens is not None:
                outputTokens += activity.outputTokens

        return outputTokens

    @classmethod
    def countOfAllInputTokens(cls):
        chats = session.query(ChatActivity).all()
        inputTokens = 1

        for chat in chats:
            if chat.inputTokens is not None:
                inputTokens += chat.inputTokens

        return inputTokens

    @staticmethod
    def getTodayMessagesCount(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        return 1 if chatActivity is None else chatActivity.todaysMessages

    @staticmethod
    def getTodayImages(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        return 1 if chatActivity is None else chatActivity.todaysImages

    @staticmethod
    def getTranslatedMessageCounts(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        if chatActivity.translatedMessagesCount is None:
            chatActivity.translatedMessagesCount = 0
            session.add(chatActivity)

        session.commit()
        return chatActivity.translatedMessagesCount

    @staticmethod
    def getAllMessagesCount(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()
        return 1 if chatActivity is None else chatActivity.allMessages

    @staticmethod
    def clearAllUsersTodayMessagesAndImages():
        userActivities = session.query(ChatActivity).all()

        for chatActivity in userActivities:
            chatActivity.todaysMessages = 0
            chatActivity.todaysImages = 0

            session.add(chatActivity)

        session.commit()

    @staticmethod
    def clearTodayMessages(
            chatId
    ):
        userActivities = session.query(ChatActivity).filter_by(chatId=chatId).first()

        for chatActivity in userActivities:
            chatActivity.todaysMessages = 0
            chatActivity.todaysImages = 0

            session.add(chatActivity)

        session.commit()

    @staticmethod
    def increaseActivityField(chatId, column):
        chatActivity = ChatActivity.get(chatId=chatId)

        if chatActivity is None:
            ChatActivity(chatId=chatId).save()

        currentValue = getattr(chatActivity, column)

        ChatActivity.update(chatActivity, column, currentValue + 1)

    @staticmethod
    def increaseOutputTokens(chatId, message):
        chatActivity = ChatActivity.get(chatId=chatId)

        outputTokens = countTokenOfMessage(message)

        if chatActivity is None:
            ChatActivity(chatId=chatId).save()

        ChatActivity.update(chatActivity, "outputTokens", chatActivity.outputTokens + outputTokens)

    @classmethod
    def getLimitReachedUsers(cls):
        limitReachedUsers = session.query(ChatActivity).filter_by(todaysMessages=16).count()

        return limitReachedUsers

    @classmethod
    def getCurrentMonthUsers(cls):
        thirtyDaysAgo = datetime.now() - timedelta(days=30)

        last_30_days_records = session.query(Chat).filter(
            Chat.lastUpdated >= thirtyDaysAgo
        ).count()

        return last_30_days_records

    @classmethod
    def getTodayActiveUsers(cls):
        today_users = session.query(ChatActivity.todaysMessages).filter(
            ChatActivity.todaysMessages >= 1
        ).count()

        return today_users

    @classmethod
    def getUsersUsedOneDay(cls):

        users_one_day_usage = session.query(Chat.chatId).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) - Chat.createdAt >= timedelta(minutes=1)
        ).distinct().count()

        return users_one_day_usage

    @classmethod
    def getUsersUsedOneWeek(cls):
        users_one_day_usage = session.query(Chat.chatId).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) - Chat.createdAt >= timedelta(days=7)
        ).distinct().count()

        return users_one_day_usage

    @classmethod
    def getUsersUsedOneMonth(cls):
        users_one_day_usage = session.query(Chat.chatId).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) - Chat.createdAt >= timedelta(days=30)
        ).distinct().count()

        return users_one_day_usage

    @classmethod
    def getLatestChat(cls):
        return session.query(Chat).\
            filter(Chat.lastUpdated.isnot(None)).\
            order_by(desc(Chat.lastUpdated)).first()


class MessageManager:

    @classmethod
    def all(cls, chatId):
        messages = session.query(Message).filter_by(chatId=chatId).order_by(Message.id).all()
        listed_messages = []

        for message in messages:
            data = {"content": message.content, "role": message.role}
            listed_messages.append(data)

        return listed_messages

    @classmethod
    def saveMessage(cls, chatId, role, content, uzMessage):
        obj = Message(role=role, content=str(content),
                      uzMessage=uzMessage, chatId=chatId,
                      createdAt=datetime.now())
        obj.save()

        return {"role": role, "content": str(content), "uzMessage": uzMessage}

    @classmethod
    def userRole(cls, translatedText, instance):
        data = cls.saveMessage(instance.chat.id, "user", translatedText, instance.text)

        chat = Chat.get(instance.chat.id)
        Chat.update(chat, "lastUpdated", datetime.now())

        chatActivity = ChatActivity.getOrCreate(instance.chat.id)

        ChatActivity.update(chatActivity, "inputTokens",
                            chatActivity.inputTokens + countTokenOfMessage(translatedText))

        del data["uzMessage"]  # deleting uzMessage before it requests to openai

        return data

    @classmethod
    def assistantRole(cls, message, instance, is_translate):
        translated_message = skipCodeTranslation(message, is_translate)

        cls.saveMessage(instance.chat.id, "assistant", message, translated_message)

        return translated_message

    @classmethod
    def system_role(cls, instance):
        cls.saveMessage(instance.chat.id, "system", instance.text, None)

    @classmethod
    def systemToAllChat(cls, text):
        chats = ChatManager.all()

        for chat in chats:
            cls.saveMessage(chat.chatId, "system", text, None)

    @classmethod
    def deleteByLimit(cls, chatId):
        max_id_subquery = (
            session.query(func.max(Message.id))
            .filter(and_(Message.chatId == chatId))
            .scalar_subquery()
        )

        unique_system_messages = session.query(distinct(Message.content)).filter_by(
            role="system", chatId=chatId).all()

        for message_content, in unique_system_messages:
            messages_to_delete = session.query(Message).filter_by(role="system", chatId=chatId,
                                                                  content=message_content).all()
            for i, message in enumerate(messages_to_delete):
                if i == 0:
                    continue

                session.delete(message)

        messages = session.query(Message).filter(and_(Message.chatId == chatId,
                                                      Message.id != max_id_subquery),
                                                 Message.role != "system").order_by(Message.id).limit(1).all()

        for message in messages:
            session.delete(message)

        session.commit()

    @classmethod
    def getSystemMessages(cls):
        chat = session.query(Chat).order_by(desc(Chat.id)).first()

        messages = session.query(Message).filter_by(chatId=chat.chatId).all()
        listed_messages = []

        for message in messages:
            data = {"content": message.content, "role": message.role}

            if data["role"] == "system":
                listed_messages.append(data)

        return listed_messages

    @classmethod
    def getTodayMessagesCount(cls):
        return session.query(func.count(Message.id)). \
                filter(cast(Message.createdAt, Date) == date.today()).scalar()

