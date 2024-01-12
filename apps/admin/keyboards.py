from aiogram import types

admin_keyboards = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("📤 Xabar yuborish.!"),
            types.KeyboardButton("🤖 System xabar yuborish.!")
        ],
        [
            types.KeyboardButton("📊 Statistika.!"),
            types.KeyboardButton("🎁 Premium obuna.!")
        ],
    ], resize_keyboard=True, one_time_keyboard=True
)


cancel_keyboards = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("/cancel"),
        ],
    ], resize_keyboard=True, one_time_keyboard=True
)

sendMessageMenu = types.InlineKeyboardMarkup(row_width=1)

inlineMessage = types.InlineKeyboardButton(text="Inline bilan", callback_data="with_inline")
simpleMessage = types.InlineKeyboardButton(text="Oddiy post", callback_data="without_inline")

sendMessageMenu.add(inlineMessage)
sendMessageMenu.add(simpleMessage)


def dynamic_sendMenu(inline_keyboards):
    sendInlineMenu = types.InlineKeyboardMarkup(row_width=2)

    for kb in inline_keyboards:
        sendInlineMenu.add(types.InlineKeyboardButton(text=str(kb["name"]), url=str(kb["callback_url"])))
    
    return sendInlineMenu
