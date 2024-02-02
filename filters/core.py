from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

class IsReplyFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        
        if not message.text.startswith('/') and not message.text.endswith('.!') and not message.text.startswith('✅'):

            if message.reply_to_message is not None:
                if message.reply_to_message.from_user.is_bot:
                    return True

            return str(message.text).lower().startswith("muloqotai") or str(message.text).lower().startswith("@muloqataibot")