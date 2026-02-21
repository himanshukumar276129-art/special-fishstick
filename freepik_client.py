import requests
import base64
import os

class FreepikClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        # Default to mystic, can be flux-dev-realism, flux-dev, etc.
        self.model = model or "mystic" 
        self.base_url = "https://api.freepik.com/v1/ai/text-to-image"

    def generate_image(self, prompt):
        """Generates an image from a prompt and returns the base64 data."""
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Mystic specific payload
        payload = {
            "prompt": prompt,
            "model": self.model 
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Check for base64 response in 'data' list
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                img_obj = data['data'][0]
                if 'base64' in img_obj:
                    return f"data:image/png;base64,{img_obj['base64']}"
                elif 'url' in img_obj:
                    return img_obj['url']
            
            # Check for direct base64
            if 'base64' in data:
                 return f"data:image/png;base64,{data['base64']}"
                 
            print(f"Freepik response did not contain expected image data: {data.keys()}")
            return None

        except Exception as e:
            print(f"Error in Freepik response: {e}")
            try:
                if hasattr(e, 'response') and e.response is not None:
                    print(f"API Error Details: {e.response.text}")
            except:
                pass
            return None
