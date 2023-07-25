from bot import bot
import re

class SendAny:
    def __init__(self, message):
        self.message = message
    
    async def send_photo(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_photo(chat_id, self.message.photo[-1].file_id, caption=self.message.caption)
        
        return await bot.send_photo(chat_id, self.message.photo[-1].file_id, caption=self.message.caption, reply_markup=kb)
    
    async def send_message(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_message(chat_id, self.message.text)
        
        return await bot.send_message(chat_id, self.message.text, reply_markup=kb)


    async def send_video(self, chat_id, kb=None):
        if kb is None:
            return await bot.send_video(chat_id, video=self.message.video.file_id, caption=self.message.caption)

        return await bot.send_video(chat_id, video=self.message.video.file_id, caption=self.message.caption, reply_markup=kb)




def extract_inline_buttons(text):
    # Split the input string using the found occurrences
    text_parts = re.split(r'\./', text)
    # Remove the empty string at the beginning of the text_parts list
    text_parts = text_parts[1:]
    # Remove \n from each text part in the list using map() and re.sub()
    text_parts = list(map(lambda part: re.sub(r'\n', '', part), text_parts))

    buttons = []

    for text in text_parts:
        button_kb = text.split('-')
        buttons.append({"name": button_kb[0], "callback_url": button_kb[1]})

    return buttons

