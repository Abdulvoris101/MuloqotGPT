from aiogram import types

kb1 = types.KeyboardButton(".📊 Statistika")
kb2 = types.KeyboardButton(".📤 Xabar yuborish")
kb3 = types.KeyboardButton(".🤖 System xabar yuborish")
kb4 = types.KeyboardButton(".‼️ Xatoliklar")


admin_keyboards = types.ReplyKeyboardMarkup([
        [
            kb1,
            kb2
        ],
        [
            kb3,
            kb4
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)