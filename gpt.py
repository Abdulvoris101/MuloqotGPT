import os
import openai
from openai.error import RateLimitError, ServiceUnavailableError, InvalidRequestError
from dotenv import load_dotenv
from core.models import  Chat
import sys
from core.utils import send_event
import time

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


async def answer_ai(messages, chat_id):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return response['choices'][0]['message']['content']
    
    
    except InvalidRequestError as e:
        error = e.error["message"]
        
        if "tokens" in error:
            await  send_event(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")
            return "Kechirasiz, men sizni tushunmadim, takrorlay olasizmi?"
        else:
            await  send_event(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."


    except RateLimitError as e:
        error = e.error["message"]
        
        await send_event(f"<b>#ratelimiterror</b>\n{error}\n#type {e.error.get('type')}\n\n#openai error\n\n#user {chat_id}")
        
        time.sleep(3)
        
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"
    
    except ServiceUnavailableError as e:
        try:
            error = e.error["message"]
        except:
            error = str(e)

        await send_event(f"<b>#serviceunvavailable</b>\n#type ServiceUnavailable\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."
    

    except openai.OpenAIError as e:        
        error = e.error["message"]

        await send_event(f"<b>#all error</b>\n#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring"
    

    except Exception as e:
        # Handle other exceptions

        await send_event(f"<b>#error</b>\n{e}\n\n#exc error\n\n#user {chat_id}")

        return "Что-то пошло не так. Пожалуйста, отправьте запрос позже"

