import asyncio
from typing import List

from aiogram import types
from aiogram.exceptions import TelegramForbiddenError, TelegramUnauthorizedError, TelegramBadRequest
from apps.core.managers import ChatManager
from apps.core.models import Chat
from apps.subscription.managers import PlanManager
from bot import bot
import re


class SendAny:
    def __init__(self, message):
        self.message = message
        self.blockedUsersCount = 0
        self.receivedUsersCount = 0

    async def sendPhoto(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption)

            else:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption, reply_markup=kb)

            self.receivedUsersCount += 1

        except TelegramUnauthorizedError:
            self.blockedUsersCount += 1
        except TelegramForbiddenError:
            self.blockedUsersCount += 1
        except TelegramBadRequest:
            self.blockedUsersCount += 1
        except:
            pass

    async def sendMessage(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_message(chatId, self.message.text)
            else:
                await bot.send_message(chatId, self.message.text, reply_markup=kb)

            self.receivedUsersCount += 1

        except TelegramUnauthorizedError:
            self.blockedUsersCount += 1
        except TelegramForbiddenError:
            self.blockedUsersCount += 1
        except TelegramBadRequest:
            self.blockedUsersCount += 1
        except:
            self.blockedUsersCount += 1
            pass

    async def sendVideo(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption)
            else:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption,
                                     reply_markup=kb)

            self.receivedUsersCount += 1

        except TelegramUnauthorizedError:
            self.blockedUsersCount += 1
        except TelegramForbiddenError:
            self.blockedUsersCount += 1
        except TelegramBadRequest:
            self.blockedUsersCount += 1
        except:
            pass

    async def sendAnimation(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_animation(chatId, animation=self.message.animation.file_id, caption=self.message.caption)
            else:
                await bot.send_animation(chatId, animation=self.message.animation.file_id, caption=self.message.caption,
                                         reply_markup=kb)

            self.receivedUsersCount += 1
        except TelegramUnauthorizedError:
            self.blockedUsersCount += 1
        except TelegramForbiddenError:
            self.blockedUsersCount += 1
        except TelegramBadRequest:
            self.blockedUsersCount += 1
        except:
            pass

    async def process_user(self, chat: Chat, inlineKeyboards=None):
        await asyncio.sleep(1)
        contentTypeHandlers = {
            "text": self.sendMessage,
            "photo": self.sendPhoto,
            "video": self.sendVideo,
            "animation": self.sendAnimation
        }

        content_type = self.message.content_type
        handler = contentTypeHandlers.get(content_type)

        if handler:
            await handler(chatId=chat.chatId, kb=inlineKeyboards)

    async def sendAnyMessages(self, chats: List[Chat], reply_markup=None):
        tasks = [self.process_user(chat, reply_markup) for chat in chats]
        await asyncio.gather(*tasks)
        data = {
            "receivedUsersCount": self.receivedUsersCount,
            "blockedUsersCount": self.blockedUsersCount
        }

        return data


def fetchUsersByUserType(userType) -> List[Chat]:
    if userType == "FREE":
        chats = PlanManager.getFreePlanUsers()
    elif userType == "ALL":
        chats = ChatManager.all()
    else:
        return ChatManager.all()
    return chats


# todo: fix
def fixMessageMarkdown(text):
    code_blocks = re.findall(r"(```)", text)

    # Check if number of opening and closing backticks are equal
    if len(code_blocks) % 2 != 0:
        # Add missing closing backtick if necessary
        text += "```"

    return text













