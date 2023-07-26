from sqlalchemy import Column, Integer, String, BigInteger, JSON
from db.setup import session, Base


# Define the 'Admin' table
# 
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
