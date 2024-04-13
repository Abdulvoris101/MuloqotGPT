from aiogram.utils import keyboard

cancelBuilder = keyboard.InlineKeyboardBuilder()
cancelBuilder.button(text="❌ Bekor qilish", callback_data="cancel")
cancelMarkup = keyboard.InlineKeyboardMarkup(inline_keyboard=cancelBuilder.export())

feedbackBuilder = keyboard.InlineKeyboardBuilder()
feedbackBuilder.button(text="✏️ Izoh qoldirish", callback_data="feedback_callback")
feedbackBuilder.attach(cancelBuilder)

feedbackMarkup = keyboard.InlineKeyboardMarkup(inline_keyboard=feedbackBuilder.export())

messageBuilder = keyboard.InlineKeyboardBuilder()
messageBuilder.button(text="✨ Tarjima qilish", callback_data="translate_callback")
messageBuilder.attach(cancelBuilder)
messageMarkup = keyboard.InlineKeyboardMarkup(inline_keyboard=messageBuilder.export())


