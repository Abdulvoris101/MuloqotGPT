from .models import Chat, Message, ChatActivity
from utils import countTokenOfMessage, constants
from utils.translate import skipCodeTranslation
from utils.events import sendEvent
from filters.permission import isGroupAllowed
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, String, func, desc, and_
from datetime import datetime, timedelta
from apps.subscription.models import ChatQuota


class ChatManager:

    @classmethod
    def groupsCount(cls):
        return session.query(Chat).filter(cast(Chat.chatId, String).startswith('-')).count()

    @classmethod
    def usersCount(cls):
        return session.query(Chat).count()

    @classmethod
    def all(cls):
        return session.query(Chat).all()

    @classmethod
    def count(cls):
        return session.query(Chat).count()

    @classmethod
    async def activate(cls, message, requestType="GPT"):
        userChat = message.chat
        chatType = userChat.type
        chatObj = Chat.get(userChat.id)

        if not isGroupAllowed(chatType, userChat.id, requestType):
            return False

        if chatObj is None:
            chatObj = Chat(userChat.id, userChat.full_name, userChat.username).save()
            await sendEvent(
                f"#new\nid: {chatObj.id}\ntelegramId: {userChat.id}"
                f"\nusername: @{userChat.username}\nname: {userChat.full_name}")

        ChatActivity.getOrCreate(userChat.id)
        ChatQuota.getOrCreate(userChat.id)

        MessageProcessor.createSystemMessages(userChat.id, userChat.type)

        session.commit()

        return True

# Analytics


class ChatActivityManager:

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
    def increaseMessageStat(chatId):
        chatActivity = ChatActivity.get(chatId=chatId)

        if chatActivity is None:
            ChatActivity(chatId=chatId).save()

        ChatActivity.update(chatActivity, "allMessages", chatActivity.allMessages + 1)
        ChatActivity.update(chatActivity, "todaysMessages", chatActivity.todaysMessages + 1)

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
        currentDayRecords = session.query(Chat).filter(
            func.extract('day', Chat.lastUpdated) == datetime.now().day).count()

        return currentDayRecords

    @classmethod
    def getUsersUsedOneDay(cls):

        users_one_day_usage = session.query(Chat.chatId).filter(
            func.coalesce(Chat.lastUpdated, Chat.createdAt) - Chat.createdAt >= timedelta(days=1)
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
        text = f"I am {instance.from_user.first_name}, {instance.text}"

        data = cls.saveMessage(instance.chat.id, "user", translatedText, text)

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

        system_messages = session.query(Message).filter_by(role="system", chatId=chatId).all()

        for i, message in enumerate(system_messages):
            if i != 0:
                session.delete(message)

        messages = session.query(Message).filter(and_(Message.chatId == chatId,
                                                      Message.id != max_id_subquery),
                                                 Message.role != "system").order_by(Message.id).offset(1).limit(1).all()

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
