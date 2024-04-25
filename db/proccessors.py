import datetime
import json
from aiogram import types

gr_rule = """You are a fun assistant. Use witty remarks, light-hearted jokes, and entertaining anecdotes to make interactions more enjoyable. Keep the tone upbeat and friendly to create a delightful and engaging user experience. Ensure that humor is suitable for all audiences and sensitive to the context of the conversation"""

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
                                          chat=chat, role='system')
        elif chat.type == "private":
            for message in systemMessages:
                MessageManager.addMessage(content=message["content"], uzMessage="",
                                          chat=chat, role='system')

