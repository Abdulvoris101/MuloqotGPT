from deep_translator import GoogleTranslator, YandexTranslator
import os
import requests
import json

token = os.environ.get("YANDEX_TOKEN")


def translate_message(message, from_='uz', lang='ru'):
    translated_message = GoogleTranslator(source=from_, target=lang).translate(message)

    return translated_message


def translate_response(message, from_='auto', lang='uz'):
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    

    data = {
        "folderId": os.environ.get("FOLDER_ID"),
        "texts": [message],
        "targetLanguageCode": 'uz',
    }

    response = requests.post(url=url, data=json.dumps(data), headers={
        "Authorization": f"Api-Key {token}"
    })

    if response.json().get("code") is not None:
        return "Botda texnik nosozlik kuzatilmoqda. Yaqin orada qaytamiz"

    return response.json()['translations'][0]['text']
