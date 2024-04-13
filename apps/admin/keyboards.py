from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


adminKeyboardsBuilder = ReplyKeyboardBuilder()
adminKeyboardsBuilder.button(text="📤 Xabar yuborish.!")
adminKeyboardsBuilder.button(text="🤖 System xabar yuborish.!")
adminKeyboardsBuilder.button(text="📊 Statistika.!")
adminKeyboardsBuilder.button(text="✖️ Premiumni rad etish.!")
adminKeyboardsBuilder.adjust(2, 2, 1)

adminKeyboardsMarkup = ReplyKeyboardMarkup(keyboard=adminKeyboardsBuilder.export(),
                                           resize_keyboard=True, one_time_keyboard=True)


cancelKeyboardsBuilder = ReplyKeyboardBuilder()
cancelKeyboardsBuilder.button(text="/cancel")

cancelKeyboardsMarkup = ReplyKeyboardMarkup(keyboard=cancelKeyboardsBuilder.export(),
                                            resize_keyboard=True, one_time_keyboard=True)


sendMessageBuilder = InlineKeyboardBuilder()
sendMessageBuilder.button(text="Inline bilan", callback_data="with_inline")
sendMessageBuilder.button(text="Oddiy post", callback_data="without_inline")

sendMessageMarkup = InlineKeyboardMarkup(inline_keyboard=sendMessageBuilder.export(),
                                         resize_keyboard=True)


def getInlineMenu(inline_keyboards):
    inlineBuilder = InlineKeyboardBuilder()

    for kb in inline_keyboards:
        inlineBuilder.button(text=str(kb["name"]),
                             url=str(kb["callback_url"]))
    
    return InlineKeyboardMarkup(inline_keyboard=inlineBuilder.export())
