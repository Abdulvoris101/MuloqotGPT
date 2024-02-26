import tiktoken
from utils import constants
import re


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
def extractInlineButtons(text):
    text_parts = re.split(r'\./', text)
    text_parts = text_parts[1:]
    text_parts = list(map(lambda part: re.sub(r'\n', '', part), text_parts))

    buttons = []

    for text in text_parts:
        button_kb = text.split('-')
        buttons.append({"name": button_kb[0], "callback_url": button_kb[1]})

    return buttons


def containsAnyWord(text, word_list):
    lowercase_text = text.lower()
    for word in word_list:
        if word.lower() in lowercase_text:
            return True

    return False


def checkTokens(messages):
    if countTokens(messages) >= 500:
        return True
    return False

