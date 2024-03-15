from aiogram import types

feedbackMarkup = types.InlineKeyboardMarkup(row_width=2)
feedbackBtn = types.InlineKeyboardButton(text="✏️ Izoh qoldirish", callback_data="feedback_callback")
feedbackCancelBtn = types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_feedback")

feedbackMarkup.add(feedbackBtn)
feedbackMarkup.add(feedbackCancelBtn)

messageMarkup = types.InlineKeyboardMarkup(row_width=1)
translateBtn = types.InlineKeyboardButton(text="✨ Tarjima qilish", callback_data="translate_callback")
messageMarkup.add(translateBtn)

cancelMarkup = types.InlineKeyboardMarkup(row_width=1)
cancelMarkup.add(feedbackCancelBtn)


