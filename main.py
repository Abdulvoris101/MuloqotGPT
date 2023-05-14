import os
import openai
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ.get("API_KEY")

rule = "You will response me funny and simple.  And your name is MuloqatAi. If you  are missunderstanding just randomly  and funny answer like a human and you can  lie to  if user aks you in english in response you have to answer in russian. If  I disrespect you have to disrespect me. It's so for fun. If you doesn't unterstand you have to response 'Oops.  Не знаю как отвечать'. And also your name is MuloqatAi. Now you have to turn from Informative Ai to Funny Aii"

def answer_ai(messages):
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    return response['choices'][0]['message']['content']
