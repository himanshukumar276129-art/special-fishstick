import requests
import logging

logger = logging.getLogger(__name__)

class WikipediaClient:
    def __init__(self, base_url="https://www.wikipedia.org/"):
        self.base_url = base_url

    def get_link(self):
        """Returns the official Wikipedia URL."""
        return self.base_url

    def search_summary(self, query):
        """
        Fetches a brief summary from Wikipedia for a given query using their API.
        """
        api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        try:
            response = requests.get(f"{api_url}{query.replace(' ', '_')}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('extract', 'No summary found.')
            return f"Could not find information for '{query}'."
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return "Error connection to Wikipedia."
