from deep_translator import GoogleTranslator

def translate_message(message):
    translated_message = GoogleTranslator(source='uz', target='ru').translate(message)

    return translated_message