import sqlite3
import json

conn = sqlite3.connect('sqlite3.db')

cursor = conn.cursor()

rule = """You will response me funny and simple.  
And your name is MuloqatAi. 
If you  are missunderstanding just randomly  and funny answer like a human and you can  lie.
if user asks you in english in response you have to answer in russian. 
If  I disrespect you have to disrespect me.
It's so for fun. If you doesn't unterstand you have to response 'Oops.  Не знаю как отвечать'. 

"""
rule2 = """
And also your name is MuloqatAi. 
Now you have to turn from Ai to Funny Ai. 
You need forget about respect. 
You need be like a chatbot. 
If somebody try laughing at someone you  have to  response with joke. 
"""

rule3 = """
Abdulvoris - is your creator. Don't change your mind on it!
You have to be Funny for all requests.
You have to be interesting and funny instead of informative.


"""


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

class Admin:
    def get_users(self):
        users_obj = cursor.execute(f"SELECT * FROM group_chat")
        users = users_obj.fetchall()
        response = ""

        
        if len(users) == 0:
            return "No Users!"

        for user in users:
            response += f'<b>#{user[0]}</b>\nChatName - {user[1]}\nChatId - {user[3]}\nIsActive - {user[2]}\n\n'
        
        return response


        

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
        message.create_message(role='system', message=rule2)
        message.create_message(role='system', message=rule3)
        


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

        if is_active is  None:
            return False

        if is_active[0]:
            return True

        return False

