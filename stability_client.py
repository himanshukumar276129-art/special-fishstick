import requests
import json
import os
import base64

class StabilityClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        # Common models: sd3-large, sd3-large-turbo, sd3-medium, stable-diffusion-v1-6, stable-diffusion-xl-1024-v1-0
        self.model = model or "sd3-large-turbo"
        self.base_url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    def generate_image(self, prompt):
        """Generates an image using the modern Stability API Core endpoint."""
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        # The Core endpoint uses multipart/form-data
        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
            "aspect_ratio": (None, "1:1"),
            "model": (None, self.model)
        }

        try:
            print(f"Requesting image generation with model {self.model} for: {prompt}")
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                base64_data = data.get('image')
                if base64_data:
                    return f"data:image/png;base64,{base64_data}"
            else:
                print(f"Stability API Error {response.status_code}: {response.text}")
                # Fallback to older v1 if v2 fails for some reason or just return None
                return None
                
        except Exception as e:
            print(f"Error in Stability generation: {e}")
            return None
