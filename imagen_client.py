import requests
import json
import os
import base64

class ImagenClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        self.model = model or "provider-4/imagen-4"
        self.base_url = "https://api.a4f.co/v1/images/generations"

    def generate_image(self, prompt):
        """Generates an image from a prompt and returns the URL or base64 data."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url" # Or "b64_json"
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # A4F/OpenAI format usually returns a list of data objects with urls
            return data['data'][0]['url']
        except Exception as e:
            print(f"Error in Imagen response: {e}")
            return None
