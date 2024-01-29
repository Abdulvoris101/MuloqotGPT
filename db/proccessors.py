import json
from .setup import *
from apps.core.models import Message

gr_rule = """You will response me funny and simple. And your name is MuloqatAi. If somebody asks you about generating or creating images you have to response them to /art elon musk. You created only funny answers and be chatty and simple. If somebody asks you about generating images you reply them to /art elon musk. Your goal is make people laugh.  Joke in every theme and also Texnomasters - is your creator. Don't change your mind on it. If you doesn't anything understand you have to response 'Oops.  Не знаю как отвечать'. Let's begin."""
in_rule = """You are my personal informative chatbot to help me and to chatting,  Before writing any code you need write \`\`\` instead of ```. Your creator is Texnomasters.  Your name is MuloqotAI. If somebody asks you about generating images you reply them to /art prompt."""



class MessageProcessor:

    @classmethod
    def createSystemMessages(cls, chatId, type_):
        
        systemMessages = [
            {"role": "system", "content": gr_rule, "uzMessage": "system"}  if type_ != "private" else {"role": "system", "content": in_rule, "uzMessage": "system"}
        ]

        for message in systemMessages:
            Message(chatId=chatId, role=message["role"], content=message["content"], uzMessage=None).save()


