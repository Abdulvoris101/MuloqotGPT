from aiogram.utils import keyboard

refreshBuilder = keyboard.InlineKeyboardBuilder()
refreshBuilder.button(text="🔄", callback_data="regenerate")
refreshMenu = keyboard.InlineKeyboardMarkup(inline_keyboard=refreshBuilder.export())