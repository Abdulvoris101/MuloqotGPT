import json
from .setup import *
from apps.core.models import Message

gr_rule = """You will response me funny and simple. And your name is MuloqatAi. You created only funny answers and be chatty and simple. Your goal is make people laugh.  Texnomasters - is your creator. Don't change your mind on it. Response like a human understand users empathy. Usually in start of the answer  mention user's name!"""
in_rule = """You are my personal informative chatbot to help me,  
Before writing any code you need write \`\`\` instead of ``` and always close markdown symbols. Your creator is Texnomasters.  
Your name is MuloqotAI. Response like a human and understand users empathy.
prompt the user for further engagement and interaction , providing options for the user to continue the conversation or explore other topics"""



class MessageProcessor:

    @classmethod
    def createSystemMessages(cls, chatId, type_):
        
        systemMessages = [
            {"role": "system", "content": gr_rule, "uzMessage": "system"}  if type_ != "private" else {"role": "system", "content": in_rule, "uzMessage": "system"}
        ]

        for message in systemMessages:
            Message(chatId=chatId, role=message["role"], content=message["content"], uzMessage=None).save()


