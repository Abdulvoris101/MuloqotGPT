from .models import Chat, Message, ChatActivity
from utils import sendEvent, countTokenOfMessage, constants
from utils.translate import skip_code_translation
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, String, func, desc, and_
from datetime import datetime, timedelta
from aiogram import types
from apps.subscription.models import ChatQuota

class ChatManager:
    # Chat db queries and filters
    three_months_ago = datetime.now() - timedelta(days=90)

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
    async def activate(cls, message):
    
        telegramChat = message.chat

        chat = Chat.get(telegramChat.id)
        
        chatType = message.chat.type
        
        if chatType in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
            if message.chat.id != constants.HOST_GROUP_ID:
                return False

        if chat is None:
            chat = Chat(telegramChat.id, telegramChat.full_name, telegramChat.username).save()
            session.add(chat)
            session.commit()
            await sendEvent(f"#new\nid: {telegramChat.id}\ntelegramId: {telegramChat.id}\nusername: @{telegramChat.username}\nname: {telegramChat.full_name}")
        
        session.add(chat)
        session.commit()

        chatActivity = ChatActivity.get(telegramChat.id)

        if chatActivity is None:
            chatActivity = ChatActivity(telegramChat.id).save()
        
        chatQuota = ChatQuota.get(telegramChat.id)

        if chatQuota is None:
            chatQuota = ChatQuota(
                telegramChat.id, additionalGptRequests=0,
                additionalImageRequests=0).save()
            
            chatQuota = ChatQuota.get(telegramChat.id)
        
        MessageProcessor.createSystemMessages(telegramChat.id, telegramChat.type)

    @classmethod
    def activeUsers(cls):
        currentMonthRecords = session.query(Chat).filter(func.extract('month', Chat.lastUpdated) == datetime.now().month).count()

        return currentMonthRecords
    
    @classmethod
    def activeUsersOfDay(cls):
        currentDayRecords = session.query(Chat).filter(func.extract('day', Chat.lastUpdated) == datetime.now().day).count()

        return currentDayRecords
    
    



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
    def getTodaysMessage(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()

        if chatActivity is None:
            return 1
        
        else:
            return chatActivity.todaysMessages

    @staticmethod
    def getTodaysImages(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()

        if chatActivity is None:
            return 1
        else:
            return chatActivity.todaysImages
        
    @staticmethod
    def getAllMessagesCount(chatId):
        chatActivity = session.query(ChatActivity).filter_by(chatId=chatId).first()

        if chatActivity is None:
            return 1
        else:
            return chatActivity.allMessages
    
    @staticmethod
    def clearAllUsersTodaysMessagesAndImages():
        userActivities = session.query(ChatActivity).all()
        
        for chatActivity in userActivities:
            chatActivity.todaysMessages = 0
            chatActivity.todaysImages = 0
            
            session.add(chatActivity)
        
        session.commit()

    @staticmethod
    def clearTodaysMessages(
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
    def increaseRequestedMessage(chatId):
        chatActivity = ChatActivity.get(chatId=chatId)
        
        
        if chatActivity is None:
            ChatActivity(chatId=chatId).save()

        ChatActivity.update(chatActivity, "todays_entered_request", chatActivity.todays_entered_request + 1)

    @staticmethod
    def increaseOutputTokens(chatId, message):
        chatActivity = ChatActivity.get(chatId=chatId)
        
        outputTokens = countTokenOfMessage(message)
        
        if chatActivity is None:
            ChatActivity(chatId=chatId).save()


        ChatActivity.update(chatActivity, "outputTokens",  chatActivity.outputTokens + outputTokens)


    @classmethod
    def getLimitReachedUsers(cls):
        limitReachedUsers = session.query(ChatActivity).filter_by(todaysMessages=16).count()

        return limitReachedUsers


class MessageManager:
    # Message manager
    
    # Get all data messages

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
        
        obj = Message(role=role, content=str(content), uzMessage=uzMessage, chatId=chatId, createdAt=datetime.now())
        obj.save()
        
        return {"role": role, "content": str(content), "uzMessage": uzMessage}
    
    
    @classmethod
    def userRole(cls, translated_text, instance):
        original_message = instance.text
        
        data = cls.saveMessage(instance.chat.id, "user", translated_text, original_message)

        chat = Chat.get(instance.chat.id)

        Chat.update(chat, "lastUpdated", datetime.now())

        chatActivity = ChatActivity.get(instance.chat.id)

        inputTokens = countTokenOfMessage(translated_text)

        if chatActivity is None:
            ChatActivity(chatId=instance.chat.id).save()
            chatActivity = ChatActivity.get(instance.chat.id)


        ChatActivity.update(chatActivity, "inputTokens", chatActivity.inputTokens + inputTokens)

        del data["uzMessage"] # deleting uzMessage before it requests to openai
    
        return data

    
    @classmethod
    def assistantRole(cls, message, instance, is_translate):
        translated_message = skip_code_translation(message, instance.chat.id, is_translate) # returns uz text  
        
        cls.saveMessage(instance.chat.id, "assistant", message, translated_message)

        return translated_message

    @classmethod
    def system_role(cls, instance):
        cls.saveMessage(instance.chat.id, "system", instance.text, None)


    @classmethod
    def systemToAllchat(cls, text):
        chats = ChatManager.all()

        for chat in chats:
            cls.saveMessage(chat.chatId, "system", text, None)


    @classmethod
    def deleteByLimit(self, chatId):
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
                                                      Message.id != max_id_subquery), Message.role != "system").order_by(Message.id).offset(1).limit(1).all()
        
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

    
    