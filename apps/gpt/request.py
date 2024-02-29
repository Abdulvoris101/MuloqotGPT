from apps.core.managers import ChatActivityManager
from apps.subscription.managers import FreeApiKeyManager, ConfigurationManager
from utils import constants
from utils.events import sendError
from utils.exception import AiogramException
import json
import aiohttp


class ResponseHandler:
    def __init__(self, response, status, chatId):
        self.status = status
        self.response = response
        self.chatId = chatId

    async def handleError(self):
        error = self.response.get("error", False)

        if error:
            errorMessage = error['message']

            if self.status == 429:
                await sendError(f"<b>#error</b>\n{errorMessage}\n\n#user {self.chatId} 429")
                raise AiogramException(self.chatId,
                                       "Shoshilmang yana 5 sekund ⏳")

            else:
                raise AiogramException(self.chatId,
                                       "Chatgptda uzilish, Iltimos birozdan so'ng yana qayta urinib ko'ring")

        raise AiogramException(self.chatId,
                               "Shoshilmang yana 5 sekund ⏳")

    async def getMessage(self):
        choices = self.response.get('choices', False)

        if choices:
            ChatActivityManager.increaseMessageStat(chatId=self.chatId)
            ChatActivityManager.increaseOutputTokens(chatId=self.chatId,
                                                     message=self.response['choices'][0]['message']['content'])
            return self.response['choices'][0]['message']['content']

        return await self.handleError()


class GptRequest:
    url = "https://api.openai.com/v1/chat/completions"

    def switchApiKey(self):
        try:
            self.free_apiKey = FreeApiKeyManager.getApiKey(self.config.apikeyPosition)
        except IndexError:
            number = 0 if int(self.config.apikeyPosition) + 1 >= FreeApiKeyManager.getMaxNumber() else int(
                self.config.apikeyPosition) + 1

            ConfigurationManager.updatePosition(number)

    def __init__(self, chatId, isPremium):
        self.chatId = chatId
        self.config = ConfigurationManager.getFirst()
        self.isPremium = isPremium
        self.free_apiKey = None
        self.frequency_penalty = 1.5 if isPremium else 1
        self.switchApiKey()
        self.apiKey = constants.API_KEY if isPremium else self.free_apiKey.apiKey

    async def requestGpt(self, messages):
        try:
            async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
                freeApiKeyManager = FreeApiKeyManager
                configurationManager = ConfigurationManager

                freeApiKeyManager.increaseRequest(self.free_apiKey.id)
                freeApiKeyManager.checkAndExpireKey(self.free_apiKey.id)

                number = 0 if int(self.config.apikeyPosition) + 1 == freeApiKeyManager.getMaxNumber() else int(
                    self.config.apikeyPosition) + 1

                configurationManager.updatePosition(number)

                headers = {
                    "Authorization": f"Bearer {self.apiKey}"
                }

                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": 250,
                    "frequency_penalty": self.frequency_penalty
                }

                async with session.post(self.url, headers=headers,
                                        json=data) as response:

                    response_data = await response.read()
                    status = response.status

                response_data = json.loads(response_data)

                response = ResponseHandler(response_data, status, self.chatId)
                response = await response.getMessage()

                return response

        except aiohttp.ClientError as e:
            await sendError(f"<b>#error</b>\n{e}\n\\n#user {self.chatId}")
            raise AiogramException(self.chatId,
                                   "Shoshilmang yana 5 sekund ⏳")

        except Exception as e:
            await sendError(f"<b>#error</b>\n{e}\n\\n#user {self.chatId}")
            raise AiogramException(self.chatId,
                                   "Chatgptda uzilish, Iltimos birozdan so'ng yana qayta urinib ko'ring")