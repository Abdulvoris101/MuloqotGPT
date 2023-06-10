from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger, JSON
from db.setup import Base, session


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    username = Column(String, nullable=True)
    is_activated = Column(Boolean)
    chat_id = Column(BigInteger)

    def __init__(self, chat_id, chat_name, username):
        self.chat_name = chat_name
        self.chat_id = chat_id
        self.username = username
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

    def activate(self, type_):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()

        if chat is None:
            chat = Chat.create(self.chat_id, self.chat_name, self.username, type_)

        chat.is_activated = True
        session.add(chat)
        session.commit()




    
class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    data = Column(JSON)
    chat_id = Column(BigInteger)

    @classmethod
    def all(cls, chat_id):
        messages = session.query(Message.data).filter_by(chat_id=chat_id).all()

        msgs = [{k: v for k, v in data.items() if k != "uz_message"} for (data,) in messages]
        return msgs

    def save(self):
        session.add(self)
        session.commit()

    @classmethod
    def user_role(cls, content, instance):
        chat_id = instance.chat.id
        
        data = {"role": "user", "content": content, "uz_message": instance.text}

        obj = cls(data=data, chat_id=chat_id)

        obj.save()
        del data["uz_message"]
        return data

    @classmethod
    def assistant_role(cls, content, instance):
        from core.utils import translate_response

        chat_id = instance.chat.id


        if len(content) > 4095:
            non_charachters = len(content) - 4050
            content = content[:-non_charachters]

        uz_message = translate_response(content)

        data = {"role": "assistant", "content": content, "uz_message": uz_message}

        obj = cls(data=data, chat_id=chat_id)

        obj.save()

        return uz_message

    @classmethod
    def system_role(cls, instance):
        chat_id = instance.chat.id

        data = {"role": "assistant", "content": instance.text, "uz_message": "system"}
        obj = cls(data=data, chat_id=chat_id)

        obj.save()

        return obj

    @classmethod
    def count(cls):
        return session.query(Message).count()

    @classmethod
    def delete_by_limit(self, chat_id):
        messages = session.query(Message).filter_by(chat_id=chat_id).order_by(Message.id).offset(4).limit(10).all()
        
        for message in messages:
            session.delete(message)

