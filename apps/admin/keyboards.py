from aiogram import types

adminKeyboards = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("📤 Xabar yuborish.!"),
            types.KeyboardButton("🤖 System xabar yuborish.!")
        ],
        [
            types.KeyboardButton("📊 Statistika.!"),
            types.KeyboardButton("🎁 Premium obuna.!")
        ],
        [
            types.KeyboardButton("✖️ Premiumni rad etish.!")
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)


cancelKeyboards = types.ReplyKeyboardMarkup([
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


def sendInlineMenu(inline_keyboards):
    inlineMenu = types.InlineKeyboardMarkup(row_width=2)

    for kb in inline_keyboards:
        inlineMenu.add(types.InlineKeyboardButton(text=str(kb["name"]), url=str(kb["callback_url"])))
    
    return inlineMenu