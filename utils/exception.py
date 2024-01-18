from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from bot import dp


class AiogramException(Exception):
    def __init__(self, user_id, message_text, original_exception=None):
        self.user_id = user_id
        self.message_text = message_text
        self.original_exception = original_exception

async def handle_custom_exception(e, message):
    # Handle the custom exception by sending a message to the user
    await message.reply(e.message_text)

async def on_error(event, e):
    if isinstance(e, AiogramException):
        await handle_custom_exception(e, event.message)
    elif isinstance(e, BotBlocked):
        # Handle specific aiogram exceptions
        print(f"Bot blocked by user: {event.from_user.id}")
    else:
        # Handle other exceptions or log them
        print(f"Unhandled exception: {type(e).__name__}, {e}")


dp.register_errors_handler(on_error)
