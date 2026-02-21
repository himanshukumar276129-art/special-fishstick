import requests
import os
import base64

class DeepAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.deepai.org/api/torch-srgan"

    def upscale_image(self, image_data_base64):
        """
        Upscale an image using DeepAI Super Resolution API.
        image_data_base64: base64 encoded image or data URL
        """
        try:
            # Handle Data URL if present
            if "," in image_data_base64:
                image_data_base64 = image_data_base64.split(",")[1]
            
            image_bytes = base64.b64decode(image_data_base64)
            
            response = requests.post(
                self.endpoint,
                files={
                    'image': ('image.png', image_bytes, 'image/png'),
                },
                headers={'api-key': self.api_key}
            )
            
            if response.status_code == 200:
                result = response.json()
                output_url = result.get("output_url")
                if output_url:
                    # Download the result and convert back to base64 if needed, 
                    # but for performance we might just return the URL or download it.
                    # The app seems to expect base64 data URLs.
                    img_response = requests.get(output_url)
                    if img_response.status_code == 200:
                        upscaled_base64 = base64.b64encode(img_response.content).decode("utf-8")
                        return f"data:image/png;base64,{upscaled_base64}"
                return None
            else:
                print(f"DeepAI Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"DeepAI Client Error: {e}")
            return None
