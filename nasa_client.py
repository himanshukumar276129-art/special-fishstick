import requests
import logging

logger = logging.getLogger(__name__)

class NASAClient:
    def __init__(self, api_key, base_url="https://api.nasa.gov/"):
        self.api_key = api_key
        self.base_url = base_url

    def get_apod(self):
        """
        Fetches the Astronomy Picture of the Day (APOD).
        Returns a dictionary with title, explanation, and image URL.
        """
        endpoint = f"{self.base_url}planetary/apod"
        params = {
            "api_key": self.api_key
        }
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title"),
                    "explanation": data.get("explanation"),
                    "url": data.get("url"),
                    "hdurl": data.get("hdurl", data.get("url")),
                    "media_type": data.get("media_type")
                }
            else:
                logger.error(f"NASA API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"NASA Client error: {e}")
            return None

    def search_images(self, query):
        """
        Searches the NASA Image and Video Library.
        """
        search_url = "https://images-api.nasa.gov/search"
        params = {
            "q": query,
            "media_type": "image"
        }
        try:
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("collection", {}).get("items", [])
                if items:
                    first_item = items[0]
                    links = first_item.get("links", [])
                    image_url = links[0].get("href") if links else None
                    title = first_item.get("data", [{}])[0].get("title")
                    description = first_item.get("data", [{}])[0].get("description")
                    return {
                        "title": title,
                        "description": description,
                        "url": image_url
                    }
            return None
        except Exception as e:
            logger.error(f"NASA Image Search error: {e}")
            return None
