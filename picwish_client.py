import requests
import os
import base64

class PicWishClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.picwish.com/api/v1/image/upscale"

    def upscale_image(self, image_data_base64):
        """
        Upscale an image using PicWish API.
        image_data_base64: base64 encoded image or data URL
        """
        try:
            # Handle Data URL if present
            if "," in image_data_base64:
                image_data_base64 = image_data_base64.split(",")[1]
            
            image_bytes = base64.b64decode(image_data_base64)
            
            headers = {
                "X-API-KEY": self.api_key,
            }
            
            files = {
                "image": ("image.png", image_bytes, "image/png")
            }
            
            # PicWish might require different parameters depending on version
            # But let's try the standard multipart upload
            response = requests.post(self.endpoint, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success" or result.get("code") == 200:
                    # PicWish usually returns a task or a direct link
                    # If it returns a data field with url
                    data = result.get("data", {})
                    output_url = data.get("image") or data.get("url")
                    
                    if output_url:
                        img_response = requests.get(output_url)
                        if img_response.status_code == 200:
                            upscaled_base64 = base64.b64encode(img_response.content).decode("utf-8")
                            return f"data:image/png;base64,{upscaled_base64}"
                else:
                    print(f"PicWish API Error: {result}")
                return None
            else:
                print(f"PicWish Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"PicWish Client Error: {e}")
            return None
