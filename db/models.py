from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Create the engine and session

try:
   engine = create_engine('postgresql://postgres:postgres@localhost:5432/muloqotai')
except Exception as error:
    print("Error while connecting to PostgreSQL:", error)


Session = sessionmaker(bind=engine)
session = Session()

# Create a base class for declarative models
Base = declarative_base()

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    is_activated = Column(Boolean)
    chat_id = Column(BigInteger)

    def __init__(self, chat_id, chat_name):
        self.chat_name = chat_name
        self.chat_id = chat_id
        super().__init__()

    @classmethod
    def all(cls):
        return session.query(Chat.id, Chat.chat_name, Chat.is_activated, Chat.chat_id).all()

    @classmethod
    def count(cls):
        return session.query(Chat.id, Chat.chat_name, Chat.is_activated, Chat.chat_id).count()


    @classmethod
    def create(cls, chat_id, chat_name, type_):
        from .proccessors import MessageProcessor

        obj = cls(chat_name=chat_name, chat_id=chat_id)

        session.add(obj)
        session.commit()

        MessageProcessor.create_system_messages(chat_id, type_)

        return obj

    def activate(self, type_):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()

        if chat is None:
            chat = Chat.create(self.chat_id, self.chat_name, type_)

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



class Error(Base):
    __tablename__ = 'error'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    
    def __init__(self, message):
        self.message = message

    @classmethod
    def all(self):
        response = []

        errors = session.query(Error).order_by(Error.id.desc()).limit(10).all()
        
        response.extend([f'<b>#{error.id}</b>\nMessage - {error.message}\n\n' for error in errors])

        return response

    def save(self):
        session.add(self)
        session.commit()



# Define the 'Admin' table
class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)

    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def is_admin(self, user_id):
        admin = session.query(Admin).filter_by(user_id=user_id).first()
        return admin is not None

    def register(self, user_id):
        if not self.__class__.is_admin(user_id):
            self.user_id = user_id
            self.save()



    def save(self):
        session.add(self)
        session.commit()



# Define the 'AdminMessage' table
class AdminMessage(Base):
    __tablename__ = 'admin_message'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)

    def __init__(self, message, message_id, chat_id):
        self.message = message
        self.message_id = message_id
        self.chat_id = chat_id

    @classmethod 
    def all(cls):
        messages = session.query(AdminMessage).all()
        response = ""

        for message in messages:
            response += f"<b>#{message.id}</b>\n<b>Message</b>: {message.message}\n"

        if len(response) == 0:
            response = "No Messages"

        return response

    
    def save(self):
        session.add(self)
        session.commit()



# Create all the tables
Base.metadata.create_all(engine)

# Commit the changes and close the session
session.commit()
