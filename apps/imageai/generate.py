from utils.translate import translateMessage
import random
import aiohttp
import asyncio
from utils.exception import AiogramException
from utils import text


class LexicaAi:
    url = "https://lexica.art/api/infinite-prompts"
    images_url = "https://image.lexica.art/full_jpg"

    @classmethod
    def getBody(cls, prompt):
        return {
            "text": prompt,
            "searchMode": "images",
            "source": "search",
            "model": "lexica-aperture-v2"
        }

    @classmethod
    async def generate(cls, userId, prompt):
        prompt = str(translateMessage(prompt, from_='auto', to='en', isTranslate=True)).strip()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        cls.url,
                        json=cls.getBody(prompt),
                        timeout=aiohttp.ClientTimeout(total=30)) as resp:

                    resp.raise_for_status()
                    images = [f"{cls.images_url}/{ids['id']}"
                              for ids in (await resp.json())["images"]]

        except asyncio.TimeoutError as e:
            raise AiogramException(user_id=userId,
                                   message_text=text.IMAGE_GEN_ERROR)

        except Exception as e:
            raise AiogramException(user_id=userId,
                                   message_text=text.IMAGE_GEN_ERROR, original_exception=e)

        return images

    @classmethod
    def getRandomImages(cls, images, num_of_images):
        random.shuffle(images)
        return images[:num_of_images]

