from apps.core.managers import ChatActivityManager
from apps.subscription.managers import FreeApiKeyManager, ConfigurationManager
from utils import sendError, constants
import json
import aiohttp


class HandleResponse:
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

                return "Shoshilmang yana 5 sekund ⏳"

            elif self.status == 500 or self.status == 503:
                return "Chatgptda uzilish, Iltimos birozdan so'ng yana qayta urinib ko'ring"

            return "Serverda xatolik. Iltimos yana bir bor ko'ring!"

        return "Serverda xatolik. Iltimos yana bir bor urinib ko'ring!"

    async def getMessage(self):

        choices = self.response.get('choices', False)

        if choices:
            ChatActivityManager.increaseMessageStat(chatId=self.chatId)
            ChatActivityManager.increaseOutputTokens(chatId=self.chatId,
                                                     message=self.response['choices'][0]['message']['content'])
            return self.response['choices'][0]['message']['content']

        return await self.handleError()


async def requestGpt(messages, chatId, is_premium):
    try:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:

            if is_premium:
                apiKey = constants.API_KEY  # premium api key
            else:

                config = ConfigurationManager.getFirst()

                try:
                    free_apiKey = FreeApiKeyManager.getApiKey(config.apikeyPosition)
                except IndexError:
                    number = 0 if int(config.apikeyPosition) + 1 >= FreeApiKeyManager.getMaxNumber() else int(
                        config.apikeyPosition) + 1

                    ConfigurationManager.updatePosition(number)

                FreeApiKeyManager.increaseRequest(free_apiKey.id)

                FreeApiKeyManager.checkAndExpireKey(free_apiKey.id)

                apiKey = free_apiKey.apiKey

                number = 0 if int(config.apikeyPosition) + 1 == FreeApiKeyManager.getMaxNumber() else int(
                    config.apikeyPosition) + 1

                ConfigurationManager.updatePosition(number)

            frequency_penalty = 1.5 if is_premium else 1

            headers = {
                "Authorization": f"Bearer {apiKey}"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 200,
                "frequency_penalty": frequency_penalty
            }

            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers,
                                    json=data) as response:

                response_data = await response.read()
                status = response.status

            response_data = json.loads(response_data)

            # Handle the response using your CleanResponse and handleResponse logic
            response = HandleResponse(response_data, status, chatId)
            response = await response.getMessage()

            return response

    except aiohttp.ClientError as e:
        print("Exception", e)

        await sendError(f"<b>#error</b>\n{e}\n\\n#user {chatId}")
        return "Shoshilmang yana 5 sekund ⏳"

    except Exception as e:
        print("Other Exception", e)
        await sendError(f"<b>#error</b>\n{e}\n\\n#user {chatId}")
        return "Serverda xatolik! Iltimos keyinroq urinib ko'ring"