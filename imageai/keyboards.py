from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


refreshMenu = InlineKeyboardMarkup(row_width=2)
regenerateBtn = InlineKeyboardButton(text="🔄", callback_data="regenerate")

refreshMenu.insert(regenerateBtn)



buyCreditMenu = InlineKeyboardMarkup(row_width=2)
buyCreditBtn = InlineKeyboardButton(text="💎 Sotib olish", callback_data="buy_credit")

buyCreditMenu.insert(buyCreditBtn)
