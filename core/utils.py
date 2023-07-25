from deep_translator import GoogleTranslator
import os
from bot import types, bot
import re
import tiktoken

def count_tokens(messages):
    enc = tiktoken.get_encoding("cl100k_base")
    token_counts = [len(enc.encode(message['content'])) for message in messages]
    total_tokens = sum(token_counts)
    return total_tokens


async def send_event(text):
    await bot.send_message(os.environ.get("EVENT_CHANNEL_ID"), text, parse_mode='HTML')


async def send_error(text):
    await bot.send_message(os.environ.get("ERROR_CHANNEL_ID"), text, parse_mode='HTML')


async def activate(message: types.Message):
    from .models import Chat

    chat = Chat(message.chat.id, message.chat.full_name, message.chat.username)
    await chat.activate(str(message.chat.type))
    

def translate_message(message, chat_id, from_='uz', lang='en'):
    from .models import Chat

    if chat_id is not None:
        is_translate = Chat.is_translate(chat_id)
    else:
        is_translate = True
    
    try:
        if is_translate:
            translated_message = GoogleTranslator(source=from_, target=lang).translate(message)
        else:
            translated_message = message
    except:
        translated_message = "Chatgpt javob bermadi. Yana bir bor urinib ko'ring"

    return translated_message


def translate_out_of_code(text, chat_id):
    # Define the pattern for identifying code blocks

    if text.find("`") == -1:
        return translate_message(text, chat_id, from_='auto', lang='uz')


    print(True)

    code_pattern = r'```.*?```'

    # Find all code blocks in the text
    code_blocks = re.findall(code_pattern, text, re.DOTALL)

    # Replace code blocks with placeholders
    for i, code_block in enumerate(code_blocks):
        text = text.replace(code_block, f'{{{{code_placeholder_{i}}}}}')

    # Translate the text outside of code blocks
    translation = translate_message(text, chat_id, 'ru', 'uz')
    translated_text = translation

    # Replace placeholders with the original code blocks
    for i, code_block in enumerate(code_blocks):
        translated_text = translated_text.replace(f'{{{{code_placeholder_{i}}}}}', code_block)

    # Return the translated text
    return translated_text
