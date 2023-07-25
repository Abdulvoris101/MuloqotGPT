from apps.core.models import Chat, Message
from faker import Faker

fake = Faker()

def fake_chat():

    for i in range(100):
        name = fake.name()

        chat_id = fake.random_int(min=10000, max=100000)

        chat = Chat(chat_id=chat_id, chat_name=name, username=fake.name(), is_activated=False)  

        chat.save()


def fake_messages():

    for i in range(100):
        Message.user_role_test("How can you?", "Salom", 5069155115)
        Message.assistant_role_test("As an AI chatbot, I'm here to provide information, answer questions, and engage in conversation. You can ask me anything you'd like, and I'll do my best to assist you. Is there something specific you would like to know or discuss?", "Sizga qanday yordam bera", 5069155115)


fake_messages()