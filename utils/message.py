import asyncio
from aiogram.utils.exceptions import BotBlocked, UserDeactivated, BotKicked
from apps.core.managers import ChatManager
from apps.subscription.managers import PlanManager
from bot import bot
import re

class SendAny:
    def __init__(self, message):
        self.message = message
        self.blockedUsersCount = 0

    async def sendPhoto(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption)
            else:
                await bot.send_photo(chatId, self.message.photo[-1].file_id,
                                     caption=self.message.caption, reply_markup=kb)
        except UserDeactivated:
            self.blockedUsersCount += 1
        except BotKicked:
            self.blockedUsersCount += 1
        except BotBlocked:
            self.blockedUsersCount += 1
        except:
            pass

    async def sendMessage(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_message(chatId, self.message.text)
            else:
                await bot.send_message(chatId, self.message.text, reply_markup=kb)
        except UserDeactivated:
            self.blockedUsersCount += 1
        except BotKicked:
            self.blockedUsersCount += 1
        except BotBlocked:
            self.blockedUsersCount += 1
        except:
            pass

    async def sendVideo(self, chatId, kb=None):
        try:
            if kb is None:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption)
            else:
                await bot.send_video(chatId, video=self.message.video.file_id, caption=self.message.caption,
                                     reply_markup=kb)
        except UserDeactivated:
            self.blockedUsersCount += 1
        except BotKicked:
            self.blockedUsersCount += 1
        except BotBlocked:
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
        except UserDeactivated:
            self.blockedUsersCount += 1
        except BotKicked:
            self.blockedUsersCount += 1
        except BotBlocked:
            self.blockedUsersCount += 1
        except:
            pass

    async def process_user(self, user, inlineKeyboards=None):

        contentTypeHandlers = {
            "text": self.sendMessage,
            "photo": self.sendPhoto,
            "video": self.sendVideo,
            "animation": self.sendAnimation
        }

        content_type = self.message.content_type
        handler = contentTypeHandlers.get(content_type)

        if handler:
            await handler(chatId=user.chatId, kb=inlineKeyboards)

    async def sendAnyMessages(self, users, inlineKeyboards=None):
        tasks = [self.process_user(user, inlineKeyboards) for user in users]
        await asyncio.gather(*tasks)

        return self.blockedUsersCount


def fetchUsersByType(contentType):
    if contentType == "FREE":
        users = PlanManager.getFreePlanUsers()
    elif contentType == "ALL":
        users = ChatManager.all()
    else:
        return False

    return users


# todo: fix
def fixMessageMarkdown(text):
    code_blocks = re.findall(r"(```)", text)

    # Check if number of opening and closing backticks are equal
    if len(code_blocks) % 2 != 0:
        # Add missing closing backtick if necessary
        text += "```"

    return text













