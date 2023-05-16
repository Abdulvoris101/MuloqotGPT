from deep_translator import GoogleTranslator

def translate_message(message, from_='uz', lang='ru'):
    translated_message = GoogleTranslator(source=from_, target=lang).translate(message)

    return translated_message
