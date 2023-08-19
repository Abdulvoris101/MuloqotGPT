import os
import openai
from openai.error import RateLimitError, ServiceUnavailableError, InvalidRequestError
from dotenv import load_dotenv
from apps.core.managers import MessageManager
from utils import send_error
import time
import httpx

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


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

            print(response.status_code)
            print(response.content)
            
            response = response.json()

            print(response)

            choices = response.get('choices', False)
            if choices:
                text = response['choices'][0]['message']['content']
                return text

            
            await send_error(f"{response.get('error')}\n\n#openai error\n\n#user {chat_id}")

            return "Iltimos 10s dan keyin qayta urinib ko'ring!"

    except httpx.RequestError as request_error:
        await send_error(f"HTTP request error: {request_error}\n\n#user {chat_id}")
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"

    except httpx.HTTPStatusError as http_status_error:
        await send_error(f"HTTP status error: {http_status_error}\n\n#user {chat_id}")
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"

    except Exception as e:
        await send_error(f"Other error: {e}\n\n#user {chat_id}")
        return "Iltimos 10s dan keyin qayta urinib ko'ring!"

    except Exception as e:
        # Handle other exceptions
        print(e)

        await send_error(f"<b>#error</b>\n{e}\n\n#exc error\n\n#user {chat_id}")

        return "Iltimos 10s dan keyin qayta urinib ko'ring!"



# except InvalidRequestError as e:
#     error = e.error["message"]
    
#     if "tokens" in error:
#         await send_error(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")
        
#         MessageManager.delete_by_limit(chat_id)

#         await "Kechirasiz, men sizni tushunmadim, takrorlay olasizmi?"
#     else:
#         await  send_error(f"#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

#     return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."

# except RateLimitError as e:
#     error = e.error["message"]
    
#     await  send_error(f"<b>#ratelimiterror</b>\n{error}\n#type {e.error.get('type')}\n\n#openai error\n\n#user {chat_id}")
    
#     time.sleep(3)
    
#     return "Iltimos 10s dan keyin qayta urinib ko'ring!"

# except ServiceUnavailableError as e:
#     try:
#         error = e.error["message"]
#     except:
#         error = str(e)

#     await send_error(f"<b>#serviceunvavailable</b>\n#type ServiceUnavailable\n{error}\n\n#openai error\n\n#user {chat_id}")

#     return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring."


# except openai.OpenAIError as e:        
#     error = e.error["message"]

#     await send_error(f"<b>#all error</b>\n#type {e.error.get('type')}\n{error}\n\n#openai error\n\n#user {chat_id}")

#     return "Chatgptda uzilish kuzatilinmoqda, Iltimos, keyinroq qayta urinib ko'ring"

