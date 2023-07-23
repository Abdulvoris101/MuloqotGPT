from sqlalchemy import create_engine, Column, select, Integer, String, UnicodeText, Boolean, BigInteger, JSON, DateTime
from db.setup import session, engine, Base
from .utils import send_event, translate_out_of_code
from sqlalchemy import not_, cast
from sqlalchemy import func
from datetime import datetime, timedelta


from datetime import datetime
    
three_months_ago = datetime.now() - timedelta(days=90)



class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    username = Column(String, nullable=True)
    is_activated = Column(Boolean)
    chat_id = Column(BigInteger)
    created_at = Column(DateTime, nullable=True)
    offset_limit = Column(BigInteger, nullable=True)
    credit = Column(BigInteger, default=50)


    def __init__(self, chat_id, chat_name, username):
        self.chat_name = chat_name
        self.chat_id = chat_id
        self.username = username
        self.created_at = datetime.now()
        self.is_activated = True
        
        super().__init__()


    @classmethod
    def all(cls):
        return session.query(Chat.id, Chat.chat_name, Chat.username, Chat.offset_limit,  Chat.is_activated, Chat.chat_id, Chat.created_at).all()

    @classmethod
    def count(cls):
        return session.query(Chat).count()
    
    @classmethod
    def groups(cls):
        return session.query(Chat).filter(cast(Chat.chat_id, String).startswith('-')).count()


    @classmethod
    def users(cls):
        return session.query(Chat).filter(not_(cast(Chat.chat_id, String).startswith('-'))).count()

    @classmethod
    def active_users(cls):
        created_at = three_months_ago.strftime('%Y-%m-%d')

        users_with_weekly_messages = (
            session.query(Chat.username)
            .join(Message, Chat.chat_id == Message.chat_id)
            .filter(Message.created_at >= three_months_ago)
            .group_by(Chat.username)
            .having(func.count(Message.id) >= 12)  # Assuming there are approximately 4 weeks in a month
            .all()
        )

        return len(users_with_weekly_messages)
    

    @classmethod
    def create(cls, chat_id, chat_name, username, type_):
        from db.proccessors import MessageProcessor

        obj = cls(chat_name=chat_name, chat_id=chat_id, username=username)

        session.add(obj)
        session.commit()

        MessageProcessor.create_system_messages(chat_id, type_)

        return obj

    
    def save(self):
        session.add(self)
        session.commit()

    async def activate(self, type_):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()
        
        if chat is None:
            chat = Chat.create(self.chat_id, self.chat_name, self.username, type_)
            await send_event(f"#new\nid: {chat.id}\ntelegramId: {self.chat_id}\nusername: @{self.username}\nname: {self.chat_name}\ntype: {type_}")

        chat.is_activated = True
        session.add(chat)
        session.commit()

    
    @classmethod
    def delete(self, chat_id):
        chat = session.query(Chat).filter_by(chat_id=chat_id).first()
        session.delete(chat)


    @classmethod
    def offset_add(self, chat_id):
        chat = session.query(Chat).filter_by(chat_id=chat_id).first()
        message_len = session.query(Message).filter_by(chat_id=chat_id).count()


        if chat is not None:
            if chat.offset_limit is not None:
                if message_len > chat.offset_limit:
                    chat.offset_limit += 10 
            else:
                chat.offset_limit = 10
            
            session.commit()
        

import json


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    data = Column(UnicodeText)
    chat_id = Column(BigInteger)
    created_at = Column(DateTime, nullable=True)

    @classmethod
    def all(cls, chat_id):
        chat = session.query(Chat).filter_by(chat_id=chat_id).first()
        offset_limit = chat.offset_limit
        query = session.query(Message.data).filter_by(chat_id=chat_id).order_by(Message.id)
        
        if offset_limit is not None:
            firstRows = query.limit(5).all()
            nextRows = query.offset(offset_limit).all()
            messages = firstRows + nextRows          
        else:
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


    def save(self):
        self.created_at = datetime.now()
        self.data = json.dumps(self.data, ensure_ascii=False)
        session.add(self)
        session.commit()


    @classmethod
    def user_role(cls, content, instance):
        chat_id = instance.chat.id
        created_at = datetime.now()
        
        data = {"role": "user", "content": str(content), "uz_message": instance.text}

        obj = cls(data=json.dumps(data, ensure_ascii=False), chat_id=chat_id, created_at=created_at)
        obj.save()

        del data["uz_message"]
        
        return data


    @classmethod
    def assistant_role(cls, content, instance):
        from core.utils import translate_message

        chat_id = instance.chat.id
        created_at = datetime.now()

        if len(content) > 4095:
            non_charachters = len(content) - 4050
            content = content[:-non_charachters]

        uz_message = translate_out_of_code(content)
        
        data = {"role": "assistant", "content": str(content), "uz_message": str(uz_message)}

        obj = cls(data=json.dumps(data, ensure_ascii=False), chat_id=chat_id, created_at=created_at)

        obj.save()

        return uz_message

    @classmethod
    def system_role(cls, instance):
        chat_id = instance.chat.id
        created_at = datetime.now()

        data = {"role": "assistant", "content": str(instance.text), "uz_message": "system"}

        obj = cls(data=json.dumps(data, ensure_ascii=False), chat_id=chat_id, created_at=created_at)

        obj.save()

        return obj

    @classmethod
    def system_to_all(cls, text):
        chats = Chat.all()
        created_at = datetime.now()

        for chat in chats:
            data = {"role": "assistant", "content": text, "uz_message": "system"}
            obj = cls(data=json.dumps(data, ensure_ascii=False), chat_id=chat[3], created_at=created_at)

            obj.save()

        return 

    @classmethod
    def count(cls):
        return session.query(Message).count()

    

    @classmethod
    def delete(self, chat_id):
        session.query(Message).filter_by(chat_id=chat_id).delete()



Base.metadata.create_all(engine)

# Commit the changes and close the session
session.commit()