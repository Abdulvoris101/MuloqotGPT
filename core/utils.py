from deep_translator import GoogleTranslator

def translate_message(message, lang='ru'):
    translated_message = GoogleTranslator(source='uz', target=lang).translate(message)

    return translated_message
