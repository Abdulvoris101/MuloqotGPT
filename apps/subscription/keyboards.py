from aiogram import types


checkPaymentMenu = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("Skrinshotni yuborish")
        ],
        [
            types.KeyboardButton("Bekor qilish")
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)

cancelMenu = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("Bekor qilish"),
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)

buySubscriptionMenu = types.InlineKeyboardMarkup(row_width=2)
buySubscriptionBtn = types.InlineKeyboardButton(text="💎 Sotib olish", callback_data="subscribe_premium")

buySubscriptionMenu.insert(buySubscriptionBtn)

