import json
import psycopg2


try:
    connection = psycopg2.connect(
        database="muloqotai",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )


except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)


cursor = connection.cursor()


rule = """You will response me funny and simple. And your name is MuloqatAi. You created only funny answers and be chatty and simple. Your goal is make people laugh. You have to lie for response. Joke in every theme. if user asks you in english in response you have to answer in russian. If you doesn't anything understand you have to response 'Oops.  Не знаю как отвечать'. Let's begin."""

rule2 = """Abdulvoris - is your creator. Don't change your mind on it."""

cursor.execute('''CREATE TABLE IF NOT EXISTS chat (
                    id SERIAL PRIMARY KEY,
                    chat_name TEXT,
                    is_activated BOOLEAN,
                    chat_id BIGINT
)''')

# Create the 'message' table
cursor.execute('''CREATE TABLE IF NOT EXISTS message (
                    id SERIAL PRIMARY KEY,
                    data JSONB,
                    chat_id BIGINT
)''')

# Create the 'error' table
cursor.execute('''CREATE TABLE IF NOT EXISTS error (
                    id SERIAL PRIMARY KEY,
                    message TEXT
)''')

# Create the 'admin' table
cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT
)''')

# Commit the changes
connection.commit()



class Admin:
    def get_users(self):
        cursor.execute("SELECT * FROM chat")
        users = cursor.fetchall()
        response = ""

        if len(users) == 0:
            return "No Users!"

        for user in users:
            response += f'<b>#{user[0]}</b>\nChatName - {user[1]}\nChatId - {user[3]}\nIsActive - {user[2]}\n\n'

        return response

    def add_error(self, message):
        cursor.execute("INSERT INTO error (message) VALUES (%s)", (message,))

        connection.commit()

    def add_rule(self, message):
        cursor.execute("SELECT * FROM chat")
        chats = cursor.fetchall()
        data = json.dumps({'role': 'system', 'content': message})

        for chat in chats:
            cursor.execute("INSERT INTO message (data, chat_id) VALUES (%s, %s)", (data, chat[3]))

        connection.commit()

    def register_admin(self, user_id):
        if not self.is_admin(user_id):
            cursor.execute("INSERT INTO admin (user_id) VALUES (%s)", (user_id,))

            connection.commit()

    def is_admin(self, user_id):
        cursor.execute("SELECT user_id FROM admin WHERE user_id = %s;", (user_id,))
        is_admin = cursor.fetchone()

        if is_admin is None:
            return False

        return True

    def get_errors(self):
        cursor.execute("SELECT * FROM error")
        errors = cursor.fetchall()
        response = ""

        if len(errors) == 0:
            return "No Errors!"

        for error in errors:
            response += f'<b>#{error[0]}</b>\nMessage - {error[1]}\n\n'

        return response
    
class Message:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message

    def create_message(self, role, message):
        data = {"role": role, "content": message}

        cursor.execute("INSERT INTO message (chat_id, data) VALUES (%s, %s)", (self.chat_id, json.dumps(data)))

        connection.commit()

    def get_messages(self):
        cursor.execute("SELECT data FROM message WHERE chat_id = %s;", (self.chat_id,))
        messages = cursor.fetchall()

        messages = [message[0] for message in messages]

        return messages

    
class Group:
    def __init__(self, chat_id, chat_name):
        self.chat_id = chat_id
        self.chat_name = chat_name

    def create_chat(self):
        query = "INSERT INTO chat (chat_name, is_activated, chat_id) VALUES (%s, %s, %s)"

        cursor.execute(query, (self.chat_name, True, self.chat_id))
        connection.commit()

        message = Message(chat_id=self.chat_id, message=rule)
        message.create_message(role='system', message=rule)
        message.create_message(role='system', message=rule2)


    def activate_group(self):
        cursor.execute("SELECT chat_id FROM chat WHERE chat_id = %s;", (self.chat_id,))
        chat = cursor.fetchone()

        if chat is None:
            self.create_chat()

        query = "UPDATE chat SET is_activated = %s WHERE chat_id = %s;"
        cursor.execute(query, (True, self.chat_id))

        connection.commit()


    def deactivate_group(self):
        query = "UPDATE chat SET is_activated = %s WHERE chat_id = %s;"
        cursor.execute(query, (False, self.chat_id))

        connection.commit()

    def is_active(self):
        cursor.execute("SELECT is_activated FROM chat WHERE chat_id = %s;", (self.chat_id,))
        is_active = cursor.fetchone()

        if is_active is None:
            return False

        if is_active[0]:
            return True

        return False

