from .models import Chat
from utils import send_event
from db.setup import session
from db.proccessors import MessageProcessor


class ChatManager:

    @classmethod
    async def activate(cls, message):
        tg_user = message.chat

        chat = Chat.get(tg_user.id)
        
        if chat is None:
            chat = Chat(tg_user.id, tg_user.full_name, tg_user.username).save()
            await send_event(f"#new\nid: {chat.id}\ntelegramId: {tg_user.id}\nusername: @{tg_user.username}\nname: {tg_user.full_name}\ntype: {tg_user.type}")
        
        chat.is_activated = True
        session.add(chat)
        session.commit()
        
        MessageProcessor.create_system_messages(tg_user.id, tg_user.type)



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
    