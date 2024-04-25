from typing import Callable, Dict, Any, Awaitablefrom aiogram import BaseMiddlewarefrom aiogram.types import Message, CallbackQueryfrom apps.core.managers import ChatManagerfrom apps.core.models import ChatActivityfrom apps.subscription.managers import SubscriptionManager, PlanManagerfrom apps.subscription.models import ChatQuotafrom bot import botfrom apps.common.filters.permission import isGroupAllowedfrom utils import textclass MessageMiddleware(BaseMiddleware):    async def __call__(        self,        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],        event: Message,        data: Dict[str, Any]    ) -> Any:        data["chat"] = event.chat        data["user"] = event.from_user        if not ChatManager.isExistsByUserId(event.chat.id):            await ChatManager.register(event.chat)            ChatActivity.getOrCreate(event.chat.id)            ChatQuota.getOrCreate(event.chat.id)            SubscriptionManager.createSubscription(planId=PlanManager.getFreePlanId(), chatId=event.chat.id,                                                   isFree=True, is_paid=True)            if not isGroupAllowed(chatType=event.chat.type, chatId=event.chat.id):                return await bot.send_message(event.chat.id, text.NOT_AVAILABLE_GROUP)        return await handler(event, data)class CallbackMiddleware(BaseMiddleware):    async def __call__(            self,            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],            event: CallbackQuery,            data: Dict[str, Any]    ) -> Any:        data["chat"] = event.message.chat        data["user"] = event.from_user        chat = event.message.chat        if not ChatManager.isExistsByUserId(chat.id):            await ChatManager.register(chat)            ChatActivity.getOrCreate(chat.id)            ChatQuota.getOrCreate(chat.id)            SubscriptionManager.createSubscription(planId=PlanManager.getFreePlanId(), chatId=chat.id,                                                   isFree=True, is_paid=True)            if not isGroupAllowed(chatType=chat.type, chatId=chat.id):                return await bot.send_message(chat.id, text.NOT_AVAILABLE_GROUP)        return await handler(event, data)