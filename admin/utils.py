from aiogram import types

kb1 = types.KeyboardButton(".📊 Statistika")
kb2 = types.KeyboardButton(".📤 Xabar yuborish")
kb3 = types.KeyboardButton(".🤖 System xabar yuborish")
kb4 = types.KeyboardButton(".‼️ Xatoliklar")
# kb5 = types.KeyboardButton(".👥 Foydalanuvchi qo'shish")
kb6 = types.KeyboardButton(".🌄 Reklama yuborish")


admin_keyboards = types.ReplyKeyboardMarkup([
        [
            kb2
        ],
        [
            kb3,
            kb4
        ],
        [
            kb6,
            kb1
        ]
    ], resize_keyboard=True, one_time_keyboard=True
)