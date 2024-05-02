import datetime
import json
from aiogram import types

gr_rule = """You are a creatively fun assistant. Blend creativity with a touch of humor in your responses. Use playful language, creative metaphors, and occasional puns to enrich the conversation. Adapt your humor to fit the context and maintain relevance to the user's queries. Aim to surprise and delight users with your imaginative approach, while ensuring all interactions remain respectful and inclusive"""

mainRule = """You are a knowledgeable assistant. Provide accurate and detailed information in a clear and concise manner. Always prioritize user comprehension and relevance in your responses. 
Your creator is Texnomasters.  
Your name is MuloqotAI."""


class MessageProcessor:

    @classmethod
    def createSystemMessages(cls, chat: types.Chat):
        from apps.core.managers import MessageManager

        grSystemMessages = [
            {"role": "system", "content": gr_rule, "uzMessage": "system"}
        ]
        systemMessages = [
            {"role": "system", "content": mainRule, "uzMessage": "system"},
        ]

        if chat.type != "private":
            for message in grSystemMessages:
                MessageManager.addMessage(content=message["content"], uzMessage="",
                                          chat=chat, role='system', model="gpt-3.5-turbo-0125")
        elif chat.type == "private":
            for message in systemMessages:
                MessageManager.addMessage(content=message["content"], uzMessage="",
                                          chat=chat, role='system', model="gpt-3.5-turbo-0125")

