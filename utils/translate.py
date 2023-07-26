from deep_translator import GoogleTranslator
import re


def translate_message(message, chat_id, from_='uz', lang='en'):
    from apps.core.models import Chat

    if chat_id is not None:
        is_translate = Chat.get(chat_id).auto_translate
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


def skip_code_translation(text, chat_id):
    # Define the pattern for identifying code blocks

    if text.find("`") == -1:
        return translate_message(text, chat_id, from_='auto', lang='uz')

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
