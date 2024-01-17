from apps.core.managers import MessageStatManager
from apps.subscription.managers import FreeApiKeyManager, ConfigurationManager
from utils import send_error, constants
import httpx
import json
import aiohttp
import time





class HandleResponse:
    def __init__(self, response, status, chat_id):
        self.status = status
        self.response = response
        self.chat_id = chat_id

    async def handleError(self):
        error = self.response.get("error", False)
        
        if error:
            errorMessage = error['message']

            if self.status == 429:
                await send_error(f"<b>#error</b>\n{errorMessage}\n\n#user {self.chat_id} 429")

                return "Shoshilmang yana 5 sekund ⏳"

            elif self.status == 500 or self.status == 503:
                return "Chatgptda uzilish, Iltimos birozdan so'ng yana qayta urinib ko'ring"
            

            return "Serverda xatolik. Iltimos yana bir bor ko'ring!"

        return "Serverda xatolik. Iltimos yana bir bor urinib ko'ring!"



    async def getContent(self):
    
        choices = self.response.get('choices', False)


        if choices:
            MessageStatManager.increaseMessageStat(chat_id=self.chat_id)
            MessageStatManager.increaseOutputTokens(chat_id=self.chat_id, message=self.response['choices'][0]['message']['content'])
            return self.response['choices'][0]['message']['content']
        

        return await self.handleError()



async def request_gpt(messages, chat_id, is_premium):
    try:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
            
            if is_premium:
                api_key = constants.API_KEY #premium api key
            else:
                
                config = ConfigurationManager.getFirst() 


                try:
                    free_api_key = FreeApiKeyManager.getApiKey(config.apikey_position)
                except IndexError:
                    number = 0 if int(config.apikey_position) + 1 >= FreeApiKeyManager.getMaxNumber() else int(config.apikey_position) + 1
                    
                    ConfigurationManager.updatePosition(number)

                print(free_api_key.id)

                FreeApiKeyManager.increaseRequest(free_api_key.id)

                FreeApiKeyManager.checkAndExpireKey(free_api_key.id)

                api_key = free_api_key.api_key
                
                number = 0 if int(config.apikey_position) + 1 == FreeApiKeyManager.getMaxNumber() else int(config.apikey_position) + 1
                
                ConfigurationManager.updatePosition(number)
                
                
            
            frequency_penalty = 1 if is_premium else 0
            
            headers = {
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 200,
                "frequency_penalty": frequency_penalty
            }

            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:

                response_data = await response.read()
                status = response.status
            
            
            response_data = json.loads(response_data)
            
            # Handle the response using your CleanResponse and handleResponse logic
            response = HandleResponse(response_data, status, chat_id)
            response = await response.getContent()
            
            return response

    except aiohttp.ClientError as e:
        print("Exception", e)

        await send_error(f"<b>#error</b>\n{e}\n\\n#user {chat_id}")
        return "Shoshilmang yana 5 sekund ⏳"

    except Exception as e:
        print("Other Exception", e)
        await send_error(f"<b>#error</b>\n{e}\n\\n#user {chat_id}")
        return "Qayta urinib ko'ring!"


