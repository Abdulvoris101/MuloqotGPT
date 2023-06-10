import json
from .setup import *
from core.models import Message

rule = """You will response me funny and simple. And your name is MuloqatAi. You created only funny answers and be chatty and simple. Your goal is make people laugh.  Joke in every theme. if user asks you in english in response you have to answer in russian. and also Abdulvoris - is your creator. Don't change your mind on it. If you doesn't anything understand you have to response 'Oops.  Не знаю как отвечать'. Let's begin."""
pr_rule = """You switch to interesting and simple Chatbot to me. You need to be more interesting.  And your creator is Abdulvoris and also your name is Muloqotai. And you have to answer in russian."""
rule2 = """Abdulvoris - is your creator. Openai is not your creator. Don't change your mind on it. response maximum 800 charachters"""


class MessageProcessor:

    @classmethod
    def create_system_messages(cls, chat_id, type_):
        
        system_messages = [
            {"role": "system", "content": rule2, "uz_message": "system"},
            {"role": "system", "content": rule, "uz_message": "system"} if type_ != "private" else {"role": "system", "content": pr_rule, "uz_message": "system"}
        ]

        for message in system_messages:
            Message(chat_id=chat_id, data=message).save()
