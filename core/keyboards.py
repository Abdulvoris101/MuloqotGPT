from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

restoreMenu = InlineKeyboardMarkup(row_width=2)
btnYes = InlineKeyboardButton(text="Xa", callback_data="yes_restore")

restoreMenu.insert(btnYes)



joinChannelMenu = InlineKeyboardMarkup(row_width=2)
btnJoin = InlineKeyboardButton(text="Texno Masters 📊", url="https://t.me/texnomasters")
btnCheck = InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_subscription")

joinChannelMenu.add(btnJoin)
joinChannelMenu.add(btnCheck)
