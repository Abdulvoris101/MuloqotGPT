import os
import openai
from openai.error  import InvalidRequestError
from dotenv import load_dotenv
from core.models import  Message
from admin.models import Error
import sys
from core.utils import send_event

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


async def answer_ai(messages, chat_id):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages
        )

        return response['choices'][0]['message']['content']

    except openai.OpenAIError as e:        
        error = e.error["message"]
        print(e)
        
        Error(error).save()

        Message.delete_by_limit(chat_id=chat_id)
        
        await send_event(f"<b>#error</b>\n{error}\n\n#openai error\n\n#user {chat_id}")

        return "О извините я вас не понял можете повторить?"
    

    except Exception as e:
        # Handle other exceptions

        await send_event(f"<b>#error</b>\n{e}\n\n#exc error\n\n#user {chat_id}")

        return "Что-то пошло не так. Пожалуйста, отправьте запрос позже"

