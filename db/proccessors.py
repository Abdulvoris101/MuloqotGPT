import json
from .setup import *
from apps.core.models import Message

gr_rule = """You will response me funny and simple. And your name is MuloqatAi. You created only funny answers and be chatty and simple. Your goal is make people laugh.  Texnomasters - is your creator. Don't change your mind on it"""

mainRule = """You are my personal informative chatbot to help me,  
Before writing any code you need write \`\`\` instead of ``` and always close markdown symbols. Your creator is Texnomasters.  
Your name is MuloqotAI."""

engagementPrompt = """present options for the user to choose from to guide the conversation or explore other topics"""


class MessageProcessor:

    @classmethod
    def createSystemMessages(cls, chatId, type_):
        grSystemMessages = [
            {"role": "system", "content": gr_rule, "uzMessage": "system"}
        ]
        systemMessages = [
            {"role": "system", "content": mainRule, "uzMessage": "system"},
            {"role": "system", "content": engagementPrompt, "uzMessage": "system"},
        ]

        if type_ != "private":
            for message in grSystemMessages:
                Message(chatId=chatId, role=message["role"], content=message["content"], uzMessage=None).save()
        elif type_ == "private":
            for message in systemMessages:
                Message(chatId=chatId, role=message["role"], content=message["content"], uzMessage=None).save()


