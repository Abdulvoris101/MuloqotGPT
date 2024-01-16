import os
from bot import bot
import tiktoken
from utils import constants
import re

# Bot 

async def send_event(text):
    await bot.send_message(constants.EVENT_CHANNEL_ID, text, parse_mode='HTML')


async def send_error(text):
    await bot.send_message(constants.ERROR_CHANNEL_ID, text, parse_mode='HTML')


# SendAny type message

class SendAny:
    def __init__(self, message):
        self.message = message
    
    async def send_photo(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_photo(chat_id, self.message.photo[-1].file_id, caption=self.message.caption)
        
        return await bot.send_photo(chat_id, self.message.photo[-1].file_id, caption=self.message.caption, reply_markup=kb)
    
    async def send_message(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_message(chat_id, self.message.text)
        
        return await bot.send_message(chat_id, self.message.text, reply_markup=kb)


    async def send_video(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_video(chat_id, video=self.message.video.file_id, caption=self.message.caption)

        return await bot.send_video(chat_id, video=self.message.video.file_id, caption=self.message.caption, reply_markup=kb)



# Token counter

def count_tokens(messages):
    enc = tiktoken.get_encoding("cl100k_base")
    token_counts = [len(enc.encode(message['content'])) for message in messages]
    total_tokens = sum(token_counts)
    return total_tokens

def count_token_of_message(message):
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


