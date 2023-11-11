from .models import Chat, Message
from utils import send_event, count_tokens, count_token_of_message
from utils.translate import skip_code_translation
from db.setup import session
from db.proccessors import MessageProcessor
from sqlalchemy import cast, String, not_, func, desc
from datetime import datetime, timedelta
import json

class ChatManager:
    # Chat db queries and filters
    three_months_ago = datetime.now() - timedelta(days=90)

    @classmethod
    def groups(cls):
        return session.query(Chat).filter(cast(Chat.chat_id, String).startswith('-')).count()

    @classmethod
    def users(cls):
        return session.query(Chat).filter(not_(cast(Chat.chat_id, String).startswith('-'))).count()

    @classmethod
    def all(cls):
        return session.query(Chat).all()

    @classmethod
    def count(cls):
        return session.query(Chat).count()
    
    @classmethod
    async def activate(cls, message):
        try:
            tg_user = message.message.chat
        except:
            tg_user = message.chat

        chat = Chat.get(tg_user.id)
        
        if chat is None:
            chat = Chat(tg_user.id, tg_user.full_name, tg_user.username).save()
            session.add(chat)
            session.commit()
            await send_event(f"#new\nid: {chat.id}\ntelegramId: {tg_user.id}\nusername: @{tg_user.username}\nname: {tg_user.full_name}\ntype: {tg_user.type}")
        
        chat.is_activated = True
        session.add(chat)
        session.commit()
        
        MessageProcessor.create_system_messages(tg_user.id, tg_user.type)

    @classmethod
    def active_users(cls):
        current_month_records = session.query(Chat).filter(func.extract('month', Chat.last_updated) == datetime.now().month).count()

        return current_month_records
    
    



class MessageManager:
    # Message manager
    
    # Get all data messages

    
    @classmethod
    def count_of_all_output_tokens(cls):
        chats = ChatManager.all()
        output_tokens_counts = 1

        for chat in chats:
            
            if chat.output_tokens_count is not None:
                output_tokens_counts += chat.output_tokens_count

        return output_tokens_counts


    @classmethod
    def count_of_all_input_tokens(cls):
        chats = ChatManager.all()
        input_tokens_counts = 1

        for chat in chats:
            
            if chat.input_tokens_count is not None:
                input_tokens_counts += chat.input_tokens_count

        return input_tokens_counts
    

    @classmethod
    def all(cls, chat_id):
        messages = session.query(Message.data).filter_by(chat_id=chat_id).order_by(Message.id).all()

        msgs = []
        
        for (data,) in messages:
            data_dict = json.loads(data)

            if not isinstance(data_dict, dict):
                msg = {k: v for k, v in eval(data_dict).items() if k != "uz_message"}
            else:
                msg = {k: v for k, v in data_dict.items() if k != "uz_message"}

            msgs.append(msg)    

        return msgs
    

    @classmethod
    def all_messages(cls):
        messages = session.query(Message.data).order_by(Message.id).all()

        decoder = json.JSONDecoder()

        encoded_messages = []
        
        for (data,) in messages:
            encoded_data, _ = decoder.raw_decode(data)
            data_dict = eval(str(encoded_data))

            data_dict.pop("uz_message", None)

            encoded_messages.append(data_dict)

        return encoded_messages
    
    @classmethod
    def base_role(cls, chat_id, role, content, uz_message):
        data = {"role": role, "content": str(content), "uz_message": uz_message}
        obj = Message(data=json.dumps(data, ensure_ascii=False), chat_id=chat_id, created_at=datetime.now())
        obj.save()

        return data
    
    @classmethod
    def user_role(cls, translated_text, instance):

        data = cls.base_role(instance.chat.id, "user", translated_text, instance.text)

        chat = Chat.get(instance.chat.id)

        input_tokens_count = count_token_of_message(translated_text)
        
        Chat.update(chat, "last_updated", datetime.now())
        Chat.update(chat, "input_tokens_count", chat.input_tokens_count +  input_tokens_count)
        Chat.update(chat, "messages_count", chat.messages_count + 1)

        del data["uz_message"] # deleting uz_message before it requests to openai
    
        return data

    @classmethod
    def user_role_for_test(cls, translated_text, text, chat_id):

        data = cls.base_role(chat_id, "user", translated_text, text)

        chat = Chat.get(chat_id)

        Chat.update(chat, "last_updated", datetime.now())
        Chat.update(chat, "messages_count", chat.messages_count + 1)

        del data["uz_message"] # deleting uz_message before it requests to openai
    
        return data

    @classmethod
    def assistant_role_for_test(cls, translated_text, chat_id):
        uz_text = skip_code_translation(translated_text, chat_id) # returns uz text  

        cls.base_role(chat_id, "assistant", translated_text, uz_text)

        return uz_text
    
    @classmethod
    def assistant_role(cls, translated_text, instance):
        uz_text = skip_code_translation(translated_text, instance.chat.id) # returns uz text  
        
        chat = Chat.get(instance.chat.id)
        
        output_tokens_count = count_token_of_message(translated_text)
        
        Chat.update(chat, "output_tokens_count",  chat.output_tokens_count + output_tokens_count)

        cls.base_role(instance.chat.id, "assistant", translated_text, uz_text)

        return uz_text

    @classmethod
    def system_role(cls, instance):
        cls.base_role(instance.chat.id, "system", instance.text,  "system")


    @classmethod
    def system_to_allchat(cls, text):
        chats = ChatManager.all()

        for chat in chats:
            cls.base_role(chat.chat_id, "system", text, "system")


    @classmethod
    def delete_by_limit(self, chat_id):
        messages = session.query(Message).filter_by(chat_id=chat_id).order_by(Message.id).offset(4).limit(3).all()
        
        for message in messages:
            session.delete(message)
            session.commit()

    @classmethod
    def count(cls):
        return Message.count()

        
    @classmethod
    def get_system_messages(cls):
        chat = session.query(Chat).order_by(desc(Chat.id)).first()

        messages = session.query(Message.data).filter_by(chat_id=chat.chat_id).all()

        msgs = []
                
        for (data,) in messages:
            data_dict = json.loads(data)

            data_dict = json.loads(data)

            if not isinstance(data_dict, dict):
                msg = {k: v for k, v in eval(data_dict).items() if k != "uz_message"}
            else:
                msg = {k: v for k, v in data_dict.items() if k != "uz_message"}

            if msg["role"] == "system":
                msgs.append(msg)    

        return msgs 

    

class CreditManager:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get(self):
        chat = session.query(Chat.credit).filter_by(chat_id=self.chat_id).first()
        
        return chat

    def use(self, amount):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()

        if chat is None:
            return False
        
        if chat.credit < amount:
            return False
        
        chat.credit = chat.credit - amount

        chat.save()

        return True
    
    def increase(self, amount):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()
        
        
        if chat is None:
            return False

        chat.credit = chat.credit + amount
        chat.save()

    
    