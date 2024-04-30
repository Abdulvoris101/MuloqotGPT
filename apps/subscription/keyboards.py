from typing import List
from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.subscription.models import Plan

cancelBuilder = keyboard.ReplyKeyboardBuilder()
cancelBuilder.button(text="Bekor qilish")
cancelMenu = keyboard.ReplyKeyboardMarkup(keyboard=cancelBuilder.export(),
                                          resize_keyboard=True, one_time_keyboard=True)

checkPaymentBuilder = keyboard.ReplyKeyboardBuilder()
checkPaymentBuilder.button(text="Skrinshotni yuborish")
checkPaymentBuilder.attach(cancelBuilder)
checkPaymentMenu = keyboard.ReplyKeyboardMarkup(keyboard=checkPaymentBuilder.export(),
                                                resize_keyboard=True, one_time_keyboard=True)


class PlanCallback(CallbackData, prefix="plans"):
    planId: UUID
    name: str


def getSubscriptionPlansMarkup(plans: List[Plan]):
    planBuilder = InlineKeyboardBuilder()

    for plan in plans:
        planBuilder.button(text=f"{plan.title}ga o'tish", callback_data=PlanCallback(
            planId=plan.id, name="subscribe_premium"))

    planBuilder.adjust(1, 1)

    return InlineKeyboardMarkup(inline_keyboard=planBuilder.export())

