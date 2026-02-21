import requests
import os
import base64

class PicsartClient:
    def __init__(self, api_keys):
        # Support both a single string key or a list of keys
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = api_keys
        self.endpoint = "https://api.picsart.io/tools/1.0/upscale"

    def upscale_image(self, image_data_base64, upscale_factor=2):
        """
        Upscale an image using Picsart Upscale API with fallback across multiple keys.
        image_data_base64: base64 encoded image or data URL
        upscale_factor: factor byte to upscale (2, 4, 6, 8)
        """
        if not self.api_keys:
            print("Picsart Error: No API keys provided")
            return None

        # Prepare image bytes once
        try:
            if "," in image_data_base64:
                image_data_base64 = image_data_base64.split(",")[1]
            image_bytes = base64.b64decode(image_data_base64)
        except Exception as e:
            print(f"Picsart Client Error decoding image: {e}")
            return None

        # Try each API key until one succeeds
        for i, api_key in enumerate(self.api_keys):
            try:
                headers = {
                    "X-Picsart-API-Key": api_key,
                    "accept": "application/json"
                }
                
                files = {
                    "image": ("image.png", image_bytes, "image/png")
                }
                
                data = {
                    "upscale_factor": upscale_factor
                }
                
                print(f"Trying Picsart API with key {i+1}/{len(self.api_keys)}...")
                response = requests.post(self.endpoint, headers=headers, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        output_url = result.get("data", {}).get("url")
                        if output_url:
                            img_response = requests.get(output_url)
                            if img_response.status_code == 200:
                                upscaled_base64 = base64.b64encode(img_response.content).decode("utf-8")
                                return f"data:image/png;base64,{upscaled_base64}"
                    else:
                        print(f"Picsart API Error (Key {i+1}): {result}")
                elif response.status_code == 429:
                    print(f"Picsart Rate Limit hit for key {i+1}. Trying next key...")
                    continue
                else:
                    print(f"Picsart Error (Key {i+1}): {response.status_code} - {response.text}")
                    continue
                    
            except Exception as e:
                print(f"Picsart Client Error with key {i+1}: {e}")
                continue
        
        print("Picsart Error: All API keys failed")
        return None
