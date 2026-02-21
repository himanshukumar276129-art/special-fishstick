import requests
import os
import base64
from io import BytesIO

class ClipDropClient:
    def __init__(self, api_keys):
        # Support both a single string key or a list of keys
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = api_keys
        self.base_url = "https://clipdrop-api.co"

    def upscale_image(self, image_data_base64, target_width=2048, target_height=2048):
        """
        Upscale an image using ClipDrop API with fallback across multiple keys.
        """
        if not self.api_keys:
            print("ClipDrop Error: No API keys provided")
            return None

        # Prepare image bytes once
        try:
            if "," in image_data_base64:
                image_data_base64 = image_data_base64.split(",")[1]
            image_bytes = base64.b64decode(image_data_base64)
        except Exception as e:
            print(f"ClipDrop Client Error decoding image: {e}")
            return None

        # Try each API key until one succeeds
        for i, api_key in enumerate(self.api_keys):
            try:
                endpoint = f"{self.base_url}/image-upscaling/v1/upscale"
                
                headers = {
                    "x-api-key": api_key
                }
                
                files = {
                    "image_file": ("image.png", image_bytes, "image/png")
                }
                
                data = {
                    "target_width": target_width,
                    "target_height": target_height
                }
                
                print(f"Trying ClipDrop API with key {i+1}/{len(self.api_keys)}...")
                response = requests.post(endpoint, headers=headers, files=files, data=data)
                
                if response.status_code == 200:
                    # ClipDrop returns the binary image data
                    upscaled_base64 = base64.b64encode(response.content).decode("utf-8")
                    return f"data:image/png;base64,{upscaled_base64}"
                elif response.status_code == 429:
                    print(f"ClipDrop Rate Limit hit for key {i+1}. Trying next key...")
                    continue
                else:
                    print(f"ClipDrop Error (Key {i+1}): {response.status_code} - {response.text}")
                    # If it's a 4xx error (other than 429), it might be worth trying another key if it's an auth issue
                    continue
                    
            except Exception as e:
                print(f"ClipDrop Client Error with key {i+1}: {e}")
                continue
        
        print("ClipDrop Error: All API keys failed")
        return None

    def cleanup_image(self, image_data_base64, mask_data_base64):
        """
        Cleanup an image using ClipDrop API (remove objects).
        """
        # Logic for cleanup can be added if needed
        pass
