from aiogram.utils import keyboard

cancelBuilder = keyboard.ReplyKeyboardBuilder()
cancelBuilder.button(text="Bekor qilish")
cancelMenu = keyboard.ReplyKeyboardMarkup(keyboard=cancelBuilder.export(),
                                          resize_keyboard=True, one_time_keyboard=True)

checkPaymentBuilder = keyboard.ReplyKeyboardBuilder()
checkPaymentBuilder.button(text="Skrinshotni yuborish")
checkPaymentBuilder.attach(cancelBuilder)
checkPaymentMenu = keyboard.ReplyKeyboardMarkup(keyboard=checkPaymentBuilder.export(),
                                                resize_keyboard=True, one_time_keyboard=True)


buySubscriptionBuilder = keyboard.InlineKeyboardBuilder()
buySubscriptionBuilder.button(text="💎 Sotib olish", callback_data="subscribe_premium")

buySubscriptionMenu = keyboard.InlineKeyboardMarkup(inline_keyboard=buySubscriptionBuilder.export())

