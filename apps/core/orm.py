from .models import Chat
from db.setup import session

class Credit:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get(self):
        return session.query(Chat.credit).filter_by(chat_id=self.chat_id).first()

    def use(self, amount):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()

        if chat.credit < amount:
            return False
        
        chat.credit = chat.credit - amount

        chat.save()

        return True
    
    def increase(self, amount):
        chat = session.query(Chat).filter_by(chat_id=self.chat_id).first()
        chat.credit = chat.credit + amount
        chat.save()
    