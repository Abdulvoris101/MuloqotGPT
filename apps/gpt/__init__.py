import os
import openai
from openai.error import RateLimitError, ServiceUnavailableError, InvalidRequestError
from dotenv import load_dotenv
from apps.core.managers import MessageManager
from utils import send_error
import httpx
import json


load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


class CleanResponse:
    def __init__(self, response, chat_id):
        self.status = response.status_code
        self.response = response
        self.chat_id = chat_id

    async def handleError(self):
        error = self.response.get("error", False)

        if error:
            errorMessage = error['message']

            if self.status == 429:
                await send_error(f"<b>#error</b>\n{errorMessage}\n\n#user {self.chat_id}")

                return "Iltimos 10s dan keyin qayta urinib ko'ring!"

            elif self.status == 500 or self.status == 503:
                return "Chatgpt javob bermayapti, Iltimos birozdan so'ng yana qayta urinib ko'ring"
            

            return "Serverda xatolik. Iltimos kechroq yana urinib ko'ring!"

        return "Serverda xatolik. Iltimos kechroq yana urinib ko'ring!"



    async def handleResponse(self):
        self.response = json.loads(self.response.text)
        
        choices = self.response.get('choices', False)

        if choices:
            return self.response['choices'][0]['message']['content']
        

        return await self.handleError()
        




async def request_gpt(messages, chat_id):
    try:
        async with httpx.AsyncClient() as client:

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",

                headers={
                    "Authorization": f"Bearer {os.environ.get('API_KEY')}"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages
                }
            )

            response = CleanResponse(response, chat_id)
            response = await response.handleResponse()

            return response

    except Exception as e:
        # Handle other exceptions
        print("Exception", e)

        await send_error(f"<b>#error</b>\n{e}\n\\n#user {chat_id}")

        return "Iltimos 10s dan keyin qayta urinib ko'ring!"


