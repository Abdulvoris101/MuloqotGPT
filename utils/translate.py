from deep_translator import GoogleTranslator
import re
import pycld2 as cld2


def translateMessage(message, from_='uz', to='en', isTranslate=False):
    try:
        if isTranslate:
            translated_message = GoogleTranslator(source=from_, target=to).translate(message)
        else:
            translated_message = message

    except Exception as e:
        translated_message = "Chatgpt javob bermadi. Yana bir bor urinib ko'ring"

    return translated_message


def skipCodeTranslation(text, isTranslate=False):
    if text.find("`") == -1:
        return translateMessage(message=text, from_='auto',
                                to='uz', isTranslate=isTranslate)

    code_pattern = r'```.*?```'
    codeBlocks = re.findall(code_pattern, text, re.DOTALL)

    for i, codeBlock in enumerate(codeBlocks):
        text = text.replace(codeBlock, f'{{{{code_placeholder_{i}}}}}')

    translatedText = translateMessage(message=text, from_='ru',
                                      to='uz', isTranslate=isTranslate)

    for i, codeBlock in enumerate(codeBlocks):
        translatedText = translatedText.replace(f'{{{{code_placeholder_{i}}}}}', codeBlock)

    return translatedText


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
      reliable, index, top_3_choices = cld2.detect(t, bestEffort=True)

    languages = [x for x in top_3_choices]
    language = languages[0]

    return language[1]
