from aiogram.utils.exceptions import BotBlocked
from bot import dp, bot


class AiogramException(Exception):
    def __init__(self, user_id, message_text, original_exception=None):
        self.user_id = user_id
        self.message_text = message_text
        self.original_exception = original_exception


async def handle_custom_exception(error, event):
    await bot.send_message(event.message.chat.id, error.message_text)


async def on_error(event, error):
    if isinstance(error, AiogramException):
        await handle_custom_exception(error, event)
    elif isinstance(error, BotBlocked):
        print("Bot blocked by user")
    else:
        print(f"Unhandled exception: {type(e).__name__}, {e}")


dp.register_errors_handler(on_error)
