import sqlite3
import json

conn = sqlite3.connect('sqlite3.db')

cursor = conn.cursor()

rule = "You will response me funny and simple.If you  are missunderstanding just randomly  and funny answer like a human and you can  lie to  if I  ask you in english in you have to response in russian. It's so for fun. If you doesn't undesrtand you have to response 'Oops.  Не знаю как отвечать'. And also your name is MuloqatAi. Now you have to turn from AI to Funny AI. if somebody try to disrespect name of 'Abdulvoris'. tell them that he is my creator and i respect him. If somebody try to ask it's not your creator ask them 'Он мой создатель'"



cursor.execute('''CREATE TABLE IF NOT EXISTS group_chat (
                    id INTEGER PRIMARY KEY,
                    chat_name TEXT,
                    is_activated BOOLEAN,
                    chat_id BIGINTEGER
)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS message (
                    id INTEGER PRIMARY KEY,
                    data JSON,
                    chat_id BIGINTEGER
)''')

conn.commit()


class Message:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message

    def create_message(self, role, message):
        data = json.dumps({"role": role, "content": message})
        
        cursor.execute("INSERT INTO message (chat_id, data) VALUES (?,?)", (self.chat_id, data))

        conn.commit()

    def get_messages(self):
        message_obj = cursor.execute(f"SELECT data FROM message WHERE chat_id = {self.chat_id};")
        messages = message_obj.fetchall()

        messages = [json.loads(message_o) for data in messages for message_o in data]

        return messages

class Group:
    def __init__(self, chat_id, chat_name):
        self.chat_id = chat_id
        self.chat_name = chat_name

    def create_chat(self):
        query = f"INSERT INTO group_chat (chat_name, is_activated, chat_id) VALUES ('{self.chat_name}', {True}, {self.chat_id})"
        
        cursor.execute(query)

        conn.commit()

        message = Message(chat_id=self.chat_id, message=rule)
        message.create_message(role='system', message=rule)
        


    def activate_group(self):
        chat = cursor.execute(f"SELECT chat_id FROM group_chat WHERE chat_id = {self.chat_id};")

        if chat.fetchone() is None:
            self.create_chat()
        
        query = f"UPDATE group_chat SET is_activated = {True} WHERE chat_id = {self.chat_id};"

        cursor.execute(query)

        conn.commit()            

        
    
    def deactivate_group(self):        
        query = f"UPDATE group_chat SET is_activated = {False} WHERE chat_id = {self.chat_id};"

        cursor.execute(query)

        conn.commit()   

    def is_active(self):
        chat = cursor.execute(f"SELECT is_activated FROM group_chat WHERE chat_id = {self.chat_id};")
        is_active = chat.fetchone()

        if is_active is None:
            self.activate_group()  
            return True


        if is_active[0]:
            return True

        return False

