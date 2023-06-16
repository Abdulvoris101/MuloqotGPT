from sqlalchemy import create_engine, Column, Integer, String, UnicodeText, Boolean, BigInteger, JSON, DateTime
from db.setup import session, engine, Base
from .utils import send_event



from datetime import datetime
    

# Create a base class for declarative models


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    username = Column(String, nullable=True)
    is_activated = Column(Boolean)
    chat_id = Column(BigInteger)
    created_at = Column(DateTime, nullable=True)


    def __init__(self, chat_id, chat_name, username):
        self.chat_name = chat_name
        self.chat_id = chat_id
        self.username = username
        self.created_at = datetime.now()
        self.is_activated = True
        
        super().__init__()

    @classmethod
    def all(cls):
        return session.query(Chat.id, Chat.chat_name, Chat.is_activated, Chat.chat_id).all()

    @classmethod
    def count(cls):
        return session.query(Chat.id, Chat.chat_name, Chat.is_activated, Chat.chat_id).count()


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
            await send_event(f"#new\nid: {chat.id}\ntelegramId: {self.chat_id}\nusername: @{self.username}\nname: {self.chat_name}")

        chat.is_activated = True
        session.add(chat)
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
        messages = session.query(Message.data).filter_by(chat_id=chat_id).all()
        msgs = []
        
        for (data,) in messages:
            data_dict = json.loads(data)
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
        
        data = {"role": "user", "content": content, "uz_message": instance.text}

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

        uz_message = translate_message(content, from_='ru', lang='uz')

        data = {"role": "assistant", "content": content, "uz_message": uz_message}

        obj = cls(data=json.dumps(data, ensure_ascii=False), chat_id=chat_id, created_at=created_at)

        obj.save()

        return uz_message

    @classmethod
    def system_role(cls, instance):
        chat_id = instance.chat.id
        created_at = datetime.now()

        data = {"role": "assistant", "content": instance.text, "uz_message": "system"}
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
    def delete_by_limit(self, chat_id):
        messages = session.query(Message).filter_by(chat_id=chat_id).order_by(Message.id).offset(4).limit(10).all()
        
        for message in messages:
            session.delete(message)



Base.metadata.create_all(engine)

# Commit the changes and close the session
session.commit()