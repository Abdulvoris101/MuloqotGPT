from aiogram import types

feedbackMarkup = types.InlineKeyboardMarkup(row_width=2)
feedbackBtn = types.InlineKeyboardButton(text="✏️ Izoh qoldirish", callback_data="feedback_callback")
feedbackCancelBtn = types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_feedback")

feedbackMarkup.add(feedbackBtn)
feedbackMarkup.add(feedbackCancelBtn)

cancelMarkup = types.InlineKeyboardMarkup(row_width=1)
cancelMarkup.add(feedbackCancelBtn)


