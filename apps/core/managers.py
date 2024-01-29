from .models import Chat, Message, MessageStats
from utils import sendEvent, countTokens, countTokenOfMessage
from utils.translate import skip_code_translation
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, String, not_, func, desc, and_
from datetime import datetime, timedelta
import json



class ChatManager:
    # Chat db queries and filters
    three_months_ago = datetime.now() - timedelta(days=90)

    @classmethod
    def groupsCount(cls):
        return session.query(Chat).filter(cast(Chat.chatId, String).startswith('-')).count()

    @classmethod
    def usersCount(cls):
        return session.query(Chat).filter(not_(cast(Chat.chatId, String).startswith('-'))).count()

    @classmethod
    def all(cls):
        return session.query(Chat).all()

    @classmethod
    def count(cls):
        return session.query(Chat).count()
    
    @classmethod
    async def activate(cls, message):
        try:
            tgUser = message.message.chat
        except:
            tgUser = message.chat

        chat = Chat.get(tgUser.id)
        
        if chat is None:
            chat = Chat(tgUser.id, tgUser.full_name, tgUser.username).save()
            session.add(chat)
            session.commit()
            await sendEvent(f"#new\nid: {chat.id}\ntelegramId: {tgUser.id}\nusername: @{tgUser.username}\nname: {tgUser.full_name}\ntype: {tgUser.type}")
        
        chat.isActivated = True
        session.add(chat)
        session.commit()

        messageStat = MessageStats.get(tgUser.id)

        if messageStat is None:
            messageStat = MessageStats(tgUser.id).save()
                    
        MessageProcessor.createSystemMessages(tgUser.id, tgUser.type)

    @classmethod
    def activeUsers(cls):
        currentMonthRecords = session.query(Chat).filter(func.extract('month', Chat.lastUpdated) == datetime.now().month).count()

        return currentMonthRecords


class MessageStatManager:

    @classmethod
    def countOfAllOutputTokens(cls):
        messageStats = session.query(MessageStats).all()
        outputTokens = 1

        for messageStat in messageStats:
            
            if messageStat.outputTokens is not None:
                outputTokens += messageStat.outputTokens

        return outputTokens


    @classmethod
    def countOfAllInputTokens(cls):
        chats = session.query(MessageStats).all()
        inputTokens = 1

        for chat in chats:
            
            if chat.inputTokens is not None:
                inputTokens += chat.inputTokens

        return inputTokens
    
    @staticmethod
    def getTodaysMessage(chatId):
        messageStat = session.query(MessageStats).filter_by(chatId=chatId).first()

        if messageStat is None:
            return 1
        
        else:
            return messageStat.todaysMessages

    @staticmethod
    def getTodaysImages(chatId):
        messageStat = session.query(MessageStats).filter_by(chatId=chatId).first()

        if messageStat is None:
            return 1
        else:
            return messageStat.todaysImages
        
    @staticmethod
    def getAllMessagesCount(chatId):
        messageStat = session.query(MessageStats).filter_by(chatId=chatId).first()

        if messageStat is None:
            return 1
        else:
            return messageStat.allMessages
    
    @staticmethod
    def clearAllUsersTodaysMessagesAndImages():
        messageStats = session.query(MessageStats).all()
        
        for messageStat in messageStats:
            messageStat.todaysMessages = 0
            messageStat.todaysImages = 0
            
            session.add(messageStat)
        
        session.commit()

    @staticmethod
    def clearTodaysMessages(
        chatId
    ):
        messageStats = session.query(MessageStats).filter_by(chatId=chatId).first()
        
        for messageStat in messageStats:
            messageStat.todaysMessages = 0
            messageStat.todaysImages = 0
            
            session.add(messageStat)
        
        session.commit()

    @staticmethod
    def increaseMessageStat(chatId):
        messageStat = MessageStats.get(chatId=chatId)
        
        
        if messageStat is None:
            MessageStats(chatId=chatId).save()


        MessageStats.update(messageStat, "allMessages", messageStat.allMessages + 1)
        MessageStats.update(messageStat, "todaysMessages", messageStat.todaysMessages + 1)

    @staticmethod
    def increaseRequestedMessage(chatId):
        messageStat = MessageStats.get(chatId=chatId)
        
        
        if messageStat is None:
            MessageStats(chatId=chatId).save()

        MessageStats.update(messageStat, "todays_entered_request", messageStat.todays_entered_request + 1)

    @staticmethod
    def increaseOutputTokens(chatId, message):
        messageStat = MessageStats.get(chatId=chatId)
        
        outputTokens = countTokenOfMessage(message)
        
        
        if messageStat is None:
            MessageStats(chatId=chatId).save()


        MessageStats.update(messageStat, "outputTokens",  messageStat.outputTokens + outputTokens)




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

        messageStat = MessageStats.get(instance.chat.id)

        inputTokens = countTokenOfMessage(translated_text)

        if messageStat is None:
            MessageStats(chatId=instance.chat.id).save()

        MessageStats.update(messageStat, "inputTokens", messageStat.inputTokens + inputTokens)

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
        
        messages = session.query(Message).filter(and_(Message.chatId == chatId,
                                                      Message.id != max_id_subquery)).order_by(Message.id).offset(1).limit(1).all()
        
        for message in messages:
            session.delete(message)
            session.commit()

    @classmethod
    def count(cls):
        return Message.count()

    
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

    
    