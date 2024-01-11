from utils.translate import translate_message
import random
import httpx


class LexicaAi:
    url = "https://lexica.art/api/infinite-prompts"

    @classmethod
    def generate(cls, prompt):
        prompt = str(translate_message(prompt, chat_id=None, from_='auto', lang='en')).strip()

        data = {
            "text": prompt,
            "searchMode": "images",
            "source": "search",
            "model": "lexica-aperture-v2"
        }

        resp = httpx.post(cls.url, json=data)
        
        images = [f"https://image.lexica.art/full_jpg/{ids['id']}" for ids in resp.json()["images"]]

        return images


    @classmethod
    def get_random_images(cls, images, num_of_images):
        # Shuffle the array of image sources
        random.shuffle(images)
        
        # Get the first six elements from the shuffled array
        random_images = images[:num_of_images]
        
        return random_images

