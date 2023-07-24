from core.models import Chat
from faker import Faker

fake = Faker()

for i in range(10):
    name = fake.name()

    chat_id = fake.random_int(min=10000, max=100000)

    chat = Chat(chat_id=chat_id, chat_name=name, username=fake.name(), is_activated=False)  

    chat.save()