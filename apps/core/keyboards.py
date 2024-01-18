from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .models import Chat

restoreMenu = InlineKeyboardMarkup(row_width=2)
btnYes = InlineKeyboardButton(text="Xa", callback_data="yes_restore")

restoreMenu.insert(btnYes)



joinChannelMenu = InlineKeyboardMarkup(row_width=2)
btnJoin = InlineKeyboardButton(text="Texno Masters 📊", url="https://t.me/texnomasters")
btnCheck = InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_subscription")

joinChannelMenu.add(btnJoin)
joinChannelMenu.add(btnCheck)


def settingsMenu(chatId):
    settingsMenu = InlineKeyboardMarkup(row_width=2)
    is_translate = Chat.get(chatId).autoTranslate
        
    text = "Tarjimonni o'chirish" if is_translate else "Tarjimonni yoqish"
    
    toggleTranslateBtn = InlineKeyboardButton(text=text, callback_data="toggle_translate")
    closeBtn = InlineKeyboardButton(text="❌", callback_data="close")

    settingsMenu.add(toggleTranslateBtn)
    settingsMenu.add(closeBtn)

    return settingsMenu


