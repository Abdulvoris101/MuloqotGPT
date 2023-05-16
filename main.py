import os
import openai
from dotenv import load_dotenv
from db.manager import Admin

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")


def answer_ai(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return response['choices'][0]['message']['content']

    except openai.OpenAIError as e:
        
        admin = Admin()
        admin.add_error(message=e)

        return "Men AI dan vaqtincha uzilib qolganga o'xshayman 🤒. Iltimos, keyinroq so'rov yuboring."

    except Exception as e:
        # Handle other exceptions
        return "Biror narsa xatol ketdi. Iltimos, keyinroq so'rov yuboring"

