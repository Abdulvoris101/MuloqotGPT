from utils.translate import translate_message
import random
import aiohttp
import asyncio
from utils.exception import AiogramException

class LexicaAi:
    url = "https://lexica.art/api/infinite-prompts"


    

    @classmethod
    async def generate(cls, userId, prompt):
        
        try:
            prompt = str(translate_message(prompt, chatId=None, from_='auto', lang='en', is_translate=True)).strip()

            data = {
                "text": prompt,
                "searchMode": "images",
                "source": "search",
                "model": "lexica-aperture-v2"
            }

        
            async with aiohttp.ClientSession() as session:
                async with session.post(cls.url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    resp.raise_for_status()
                    images = [f"https://image.lexica.art/full_jpg/{ids['id']}" for ids in (await resp.json())["images"]]

        except asyncio.TimeoutError as e:
            raise AiogramException(user_id=userId, message_text="Xozirgi vaqtda rasm generatsiyasi ishlamayapti iltimos keyinroq urinib ko'ring!")
    
        except aiohttp.ClientConnectionError as e:
            raise AiogramException(user_id=userId, message_text="Xozirgi vaqtda rasm generatsiyasi ishlamayapti iltimos keyinroq urinib ko'ring!", original_exception=e)

        except Exception as e:
            # Handle other exceptions if needed
            raise AiogramException(user_id=userId, message_text="Rasm generatsiyasi jarayonida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.", original_exception=e)
        
        return images


    @classmethod
    def getRandomImages(cls, images, num_of_images):
        # Shuffle the array of image sources
        random.shuffle(images)
        
        # Get the first six elements from the shuffled array
        random_images = images[:num_of_images]
        
        return random_images

