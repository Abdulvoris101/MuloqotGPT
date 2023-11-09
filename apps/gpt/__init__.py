import os
import openai
from openai.error import RateLimitError, ServiceUnavailableError, InvalidRequestError
from dotenv import load_dotenv
from apps.core.managers import MessageManager
from utils import send_error
import httpx
import json
import aiohttp
import asyncio

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


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
                await send_error(f"<b>#error</b>\n{errorMessage}\n\n#user {self.chat_id}")

                return "Iltimos 10 sekund dan keyin qayta urinib ko'ring!"

            elif self.status == 500 or self.status == 503:
                return "Chatgpt javob bermayapti, Iltimos birozdan so'ng yana qayta urinib ko'ring"
            

            return "Serverda xatolik. Iltimos kechroq yana urinib ko'ring!"

        return "Serverda xatolik. Iltimos kechroq yana urinib ko'ring!"



    async def getContent(self):
    
        choices = self.response.get('choices', False)


        if choices:
            return self.response['choices'][0]['message']['content']
        

        return await self.handleError()
        




async def request_gpt(messages, chat_id):
    try:
        async with aiohttp.ClientSession() as session:
            
            headers = {
                "Authorization": f"Bearer {os.environ.get('API_KEY')}"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1000
            }


            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:
                response_data = await response.json()
                status = response.status

            # Handle the response using your CleanResponse and handleResponse logic
            response = HandleResponse(response_data, status, chat_id)
            response = await response.getContent()

            return response

    except aiohttp.ClientError as e:
        print("Exception", e)

        await send_error(f"<b>#error</b>\n{e}\n\\n#user {chat_id}")
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"

    except Exception as e:
        print("Other Exception", e)
        await send_error(f"<b>#error</b>\n{e}\n\\n#user {chat_id}")
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"


