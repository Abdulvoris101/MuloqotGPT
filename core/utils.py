from deep_translator import GoogleTranslator, YandexTranslator
import os
import requests
import json
from aiogram.dispatcher.filters import BoundFilter
from app import types, bot
import re

# token = os.environ.get("YANDEX_TOKEN")


async def send_event(text):

    await bot.send_message("-840987349", text, parse_mode='HTML')


class IsReplyFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.is_bot:
                return True

        return  str(message.text).lower().startswith("muloqotai") or str(message.text).lower().startswith("@muloqataibot")



def translate_message(message, from_='uz', lang='ru'):
    try:
        translated_message = GoogleTranslator(source=from_, target=lang).translate(message)
    except:
        translated_message = "Chatgpt javob bermadi. Yana bir bor urinib ko'ring"

    return translated_message


def translate_out_of_code(text):
    # Define the pattern for identifying code blocks


    if text.find("`") == -1:
        return translate_message(text, from_='ru', lang='uz')


    print(True)

    code_pattern = r'```.*?```'

    # Find all code blocks in the text
    code_blocks = re.findall(code_pattern, text, re.DOTALL)

    # Replace code blocks with placeholders
    for i, code_block in enumerate(code_blocks):
        text = text.replace(code_block, f'{{{{code_placeholder_{i}}}}}')

    # Translate the text outside of code blocks
    translation = translate_message(text, 'ru', 'uz')
    translated_text = translation

    # Replace placeholders with the original code blocks
    for i, code_block in enumerate(code_blocks):
        translated_text = translated_text.replace(f'{{{{code_placeholder_{i}}}}}', code_block)

    # Return the translated text
    return translated_text







    


# def ya_translate(message, lang='ru'):
#     url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    

#     data = {
#         "folderId": os.environ.get("FOLDER_ID"),
#         "texts": [message],
#         "targetLanguageCode": lang,
#     }

#     response = requests.post(url=url, data=json.dumps(data), headers={
#         "Authorization": f"Api-Key {token}"
#     })

#     if response.json().get("code") is not None:
#         return "Botda texnik nosozlik kuzatilmoqda. Yaqin orada qaytamiz"

#     return response.json()['translations'][0]['text']
