from aiogram import types


check_payment_menu = types.ReplyKeyboardMarkup([
        [
            types.KeyboardButton("Davom etish"),
            
        ],
        [
            types.KeyboardButton("/cancel"),
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)
