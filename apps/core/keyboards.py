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
messageMarkup = keyboard.InlineKeyboardMarkup(inline_keyboard=messageBuilder.export())


profileBuilder = keyboard.InlineKeyboardBuilder()
profileBuilder.button(text="🤖 Gpt modelni o'zgartirish", callback_data="change_chat_gpt_model")
profileBuilder.button(text="➕ Do'stni chaqirish (referral)", callback_data="referral_link")
profileBuilder.adjust(1, 1)
profileMarkup = keyboard.InlineKeyboardMarkup(inline_keyboard=profileBuilder.export())


gptModelsBuilder = keyboard.ReplyKeyboardBuilder()
gptModelsBuilder.button(text="gpt-3.5-turbo-0125")
gptModelsBuilder.button(text="gpt-4")
gptModelsBuilder.adjust(1, 1)
gptModelsMarkup = keyboard.ReplyKeyboardMarkup(keyboard=gptModelsBuilder.export(), resize_keyboard=True,
                                               one_time_keyboard=True)


