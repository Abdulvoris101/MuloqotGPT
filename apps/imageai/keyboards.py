from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


refreshMenu = InlineKeyboardMarkup(row_width=2)
regenerateBtn = InlineKeyboardButton(text="🔄", callback_data="regenerate")

refreshMenu.insert(regenerateBtn)


