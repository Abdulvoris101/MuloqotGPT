from deep_translator import GoogleTranslator
import re
import pycld2 as cld2


def translateMessage(message, chatId, from_='uz', lang='en', is_translate=False):
    try:
        if is_translate:
            translated_message = GoogleTranslator(source=from_, target=lang).translate(message)
        else:
            translated_message = message
    except:
        translated_message = "Chatgpt javob bermadi. Yana bir bor urinib ko'ring"

    return translated_message


def skipCodeTranslation(text, chatId, is_translate=False):
    from apps.core.models import Chat
    
    # Define the pattern for identifying code blocks
    
    if text.find("`") == -1:
        return translateMessage(text, chatId, from_='auto', lang='uz', is_translate=is_translate)

    code_pattern = r'```.*?```'

    # Find all code blocks in the text
    code_blocks = re.findall(code_pattern, text, re.DOTALL)

    # Replace code blocks with placeholders
    for i, code_block in enumerate(code_blocks):
        text = text.replace(code_block, f'{{{{code_placeholder_{i}}}}}')

    # Translate the text outside of code blocks
    translation = translateMessage(text, chatId, 'ru', 'uz', is_translate=is_translate)
    translated_text = translation

    # Replace placeholders with the original code blocks
    for i, code_block in enumerate(code_blocks):
        translated_text = translated_text.replace(f'{{{{code_placeholder_{i}}}}}', code_block)

    # Return the translated text
    return translated_text

def detect(text):
    """Decide which language is used to write the text.

    The method tries first to detect the language with high reliability. If
    that is not possible, the method switches to best effort strategy.


    Args:
      text (string): A snippet of text, the longer it is the more reliable we
                     can detect the language used to write the text.
    """
    t = text.encode("utf-8")
    reliable, index, top_3_choices = cld2.detect(t, bestEffort=False)

    if not reliable:
      reliable = False
      reliable, index, top_3_choices = cld2.detect(t, bestEffort=True)

    languages = [x for x in top_3_choices]
    language = languages[0]
    return language[1]