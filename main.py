import os
import openai
from openai.error import RateLimitError, ServiceUnavailableError, InvalidRequestError
from dotenv import load_dotenv
from core.models import  Chat
from admin.models import Error
import sys
from core.utils import send_event
import time

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


async def answer_ai(messages, chat_id):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages
        )

        return response['choices'][0]['message']['content']

    except InvalidRequestError as e:
        error = e.error["message"]
        
        Error(error).save()

        await send_event(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

        if "tokens" in error:
            await send_event(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

            Chat.offset_add(chat_id=chat_id)
            
            return "О извините я вас не понял можете повторить?"

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."



    except RateLimitError as e:
        error = e.error["message"]
        
        Error(error).save()

        await send_event(f"<b>#ratelimiterror</b>\n{error}\n#type {e.error.get('type')}\n\n#openai error\n\n#user {chat_id}")
        
        time.sleep(5)
        
        return "Iltimos 20s dan keyin qayta urinib ko'ring!"
    
    except ServiceUnavailableError as e:
        error = e.error["message"]

        Error(error).save()
    
        await send_event(f"<b>#serviceunvavailable</b>\n#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."
    

    except openai.OpenAIError as e:        
        error = e.error["message"]

        Error(error).save()

        await send_event(f"<b>#all error</b>\n#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring"
    

    except Exception as e:
        # Handle other exceptions

        await send_event(f"<b>#error</b>\n{e}\n\n#exc error\n\n#user {chat_id}")

        return "Что-то пошло не так. Пожалуйста, отправьте запрос позже"

