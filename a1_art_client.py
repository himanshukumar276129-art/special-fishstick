import requests
import os
import logging

logger = logging.getLogger(__name__)

class A1ArtClient:
    def __init__(self, api_keys, model="A1.art"):
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = [k for k in api_keys if k]
        self.model = model
        # Base URL for A1.art image generation
        self.base_url = "https://a1.art/open-api/v1/a1/images/generate"

    def generate_image(self, prompt):
        """
        Generates an image/logo from a prompt using A1.art API.
        Tries all available API keys.
        Returns the image URL or None.
        """
        if not self.api_keys:
            logger.error("A1.art API keys are missing.")
            return None

        # Enhance prompt for logo if not already specific
        if "logo" in prompt.lower() and "professional" not in prompt.lower():
            enhanced_prompt = f"Professional high-quality logo for: {prompt}. Clean, minimalist, vector style, white background."
        else:
            enhanced_prompt = prompt

        payload = {
            "prompt": enhanced_prompt,
            "model": self.model,
            "num": 1,
            "width": 1024,
            "height": 1024
        }

        for api_key in self.api_keys:
            try:
                headers = {
                    "apiKey": api_key,
                    "Content-Type": "application/json"
                }
                
                logger.info(f"🎨 A1.art Request with key {api_key[:8]}... : {enhanced_prompt}")
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code != 200:
                    logger.error(f"✗ A1.art API error ({response.status_code}) with key {api_key[:8]}: {response.text}")
                    continue # Try next key
                    
                data = response.json()
                
                # A1.art often returns results in different formats depending on the specific application
                # Common patterns: data: { url: ... } or data: [ { url: ... } ]
                image_url = None
                if 'data' in data:
                    d = data['data']
                    if isinstance(d, list) and len(d) > 0:
                        image_url = d[0].get('url') or d[0].get('imageUrl')
                    elif isinstance(d, dict):
                        image_url = d.get('url') or d.get('imageUrl')
                    elif isinstance(d, str) and (d.startswith('http') or d.startswith('data:')):
                        image_url = d
                
                if not image_url and 'imageUrl' in data:
                    image_url = data['imageUrl']
                    
                if not image_url and 'url' in data:
                    image_url = data['url']

                if image_url:
                    return image_url

                logger.error(f"✗ A1.art response did not contain an image URL with key {api_key[:8]}: {data}")
                
            except Exception as e:
                logger.error(f"✗ A1.art key {api_key[:8]} critical error: {e}")
                continue # Try next key

        return None
