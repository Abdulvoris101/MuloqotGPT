from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

restoreMenu = InlineKeyboardMarkup(row_width=2)
btnYes = InlineKeyboardButton(text="Xa", callback_data="yes_restore")

restoreMenu.insert(btnYes)
