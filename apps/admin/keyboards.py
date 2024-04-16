from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


adminKeyboardsBuilder = InlineKeyboardBuilder()
adminKeyboardsBuilder.button(text="➡️ Xabar yuborish", callback_data="send_message_to_users")
adminKeyboardsBuilder.button(text="📈 Statistika", callback_data="statistics")
adminKeyboardsBuilder.button(text="🎁 Premium obuna", callback_data="give_premium")
adminKeyboardsBuilder.button(text="✖️ Premiumni rad etish", callback_data="reject_subscription_request")
adminKeyboardsBuilder.adjust(2, 2)

adminKeyboardsMarkup = InlineKeyboardMarkup(inline_keyboard=adminKeyboardsBuilder.export())


class ConfirmSubscriptionCallback(CallbackData, prefix="subscription"):
    receiverId: int
    name: str


def getConfirmSubscriptionMarkup(receiverId: int):
    confirmSubscriptionBuilder = InlineKeyboardBuilder()

    confirmSubscriptionBuilder.button(text="Xa", callback_data=ConfirmSubscriptionCallback(
        receiverId=receiverId, name="subscribe_yes"))

    confirmSubscriptionBuilder.button(text="Yo'q", callback_data="cancel")

    return InlineKeyboardMarkup(inline_keyboard=confirmSubscriptionBuilder.export())


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
