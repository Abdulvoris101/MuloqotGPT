import os
from bot import bot
import tiktoken
from utils import constants
import re
from aiogram.utils.exceptions import BotBlocked

# Bot 

async def sendEvent(text):
    await bot.send_message(constants.EVENT_CHANNEL_ID, text, parse_mode='HTML')


async def sendSubscriptionEvent(text):
    await bot.send_message(constants.SUBSCRIPTION_CHANNEL_ID, text, parse_mode='HTML')


async def sendError(text):
    await bot.send_message(constants.ERROR_CHANNEL_ID, text, parse_mode='HTML')


# SendAny type message

class SendAny:
    def __init__(self, message):
        self.message = message
    
    async def sendPhoto(self, chatId, kb=None):
        
        try:  
            if kb is None:
                return await bot.send_photo(chatId, self.message.photo[-1].file_id, caption=self.message.caption)
            
            return await bot.send_photo(chatId, self.message.photo[-1].file_id, caption=self.message.caption, reply_markup=kb)
        except BotBlocked:
            print("Bot blocked")
            
    async def send_message(self, chatId, kb=None):
        try:
                
            if kb is None:
                return await bot.send_message(chatId, self.message.text)
            
            return await bot.send_message(chatId, self.message.text, reply_markup=kb)

        except BotBlocked:
            print("Bot blocked")

    async def send_video(self, chatId, kb=None):
        try:
            if kb is None:
                return await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption)

            return await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption, reply_markup=kb)
        except BotBlocked:
            print("Bot blocked")


# Token counter

def countTokens(messages):
    enc = tiktoken.get_encoding("cl100k_base")
    token_counts = [len(enc.encode(message['content'])) for message in messages]
    total_tokens = sum(token_counts)
    return total_tokens

def countTokenOfMessage(message):
    enc = tiktoken.get_encoding("cl100k_base")
    total_tokens = len(enc.encode(message))
    
    return total_tokens


# Extract inline buttons

def extract_inline_buttons(text):
    # Split the input string using the found occurrences
    text_parts = re.split(r'\./', text)
    # Remove the empty string at the beginning of the text_parts list
    text_parts = text_parts[1:]
    # Remove \n from each text part in the list using map() and re.sub()
    text_parts = list(map(lambda part: re.sub(r'\n', '', part), text_parts))

    buttons = []

    for text in text_parts:
        button_kb = text.split('-')
        buttons.append({"name": button_kb[0], "callback_url": button_kb[1]})

    return buttons


