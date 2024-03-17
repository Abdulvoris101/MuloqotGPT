from utils.translate import translateMessage
import random
import aiohttp
import asyncio
from utils.exception import AiogramException
from utils import text
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession


class ImageGen:
    url = "https://deepdreamgenerator.com/search-text"

    @classmethod
    def getBody(cls, prompt):
        return {
            "q": prompt,
            "offset": 0,
        }

    @classmethod
    def parse(cls, src):
        soup = BeautifulSoup(src, "lxml")
        images = soup.find_all("img", class_="lazyload")

        return [image.get("data-src") for image in images]

    @classmethod
    async def generate(cls, userId, prompt):
        prompt = str(translateMessage(prompt, from_='auto', to='en', isTranslate=True)).strip()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=cls.url,
                        json=cls.getBody(prompt),
                        timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    htmlResponse = (await resp.json())["results"]
                    images = cls.parse(htmlResponse)

        except asyncio.TimeoutError as e:
            raise AiogramException(userId=userId, message_text=text.IMAGE_GEN_ERROR)

        except aiohttp.client.ClientResponseError as e:
            raise AiogramException(userId=userId, message_text=text.IMAGE_GEN_ERROR)

        except Exception as e:
            raise AiogramException(userId=userId, message_text=text.IMAGE_GEN_ERROR)

        return images

    @classmethod
    def getRandomImages(cls, images, num_of_images):
        random.shuffle(images)
        return images[:num_of_images]

