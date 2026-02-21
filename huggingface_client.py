import requests
import os
import base64
import time

class HuggingFaceClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        # Default to a popular model, can be changed
        self.model = model or "stabilityai/stable-diffusion-3.5-large" 
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}"

    def generate_image(self, prompt):
        """Generates an image from a prompt and returns the base64 data."""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "inputs": prompt,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Hugging Face returns the raw image bytes
            image_bytes = response.content
            
            # Convert to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"

        except Exception as e:
            print(f"Error in HuggingFace response: {e}")
            try:
                if hasattr(e, 'response') and e.response is not None:
                    print(f"API Error Details: {e.response.text}")
            except:
                pass
    def generate_video(self, prompt, image_url=None):
        """Generates a video from a prompt using Hugging Face Inference API."""
        # Use a reliable public text-to-video model
        video_model = "cerspense/zeroscope_v2_576w"
        api_url = f"https://api-inference.huggingface.co/models/{video_model}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "inputs": prompt,
        }

        try:
            print(f"HF Video: Requesting {video_model}...")
            
            # Use a loop to handle loading status
            max_hf_retries = 3
            for hf_attempt in range(max_hf_retries):
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                
                # Check for "model loading" response
                if response.status_code == 200 and response.headers.get('content-type') == 'application/json':
                    json_data = response.json()
                    if isinstance(json_data, dict) and 'estimated_time' in json_data:
                        wait_time = json_data.get('estimated_time', 20)
                        print(f"HF Video: Model is loading, waiting {wait_time}s (Attempt {hf_attempt+1})")
                        time.sleep(min(wait_time, 30))
                        continue
                    if 'error' in json_data:
                        print(f"HF Video Error: {json_data}")
                        return None
                
                response.raise_for_status()
                
                # HF returns raw bytes for video
                video_bytes = response.content
                
                # Save to a temporary public file
                timestamp = int(time.time())
                filename = f"hf_video_{timestamp}.mp4"
                
                # Ensure static/generated directory exists
                output_dir = os.path.join(os.getcwd(), 'static', 'generated')
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                output_path = os.path.join(output_dir, filename)
                
                with open(output_path, 'wb') as f:
                    f.write(video_bytes)
                    
                print(f"HF Video saved to {output_path}")
                
                # Return web-accessible URL
                return f"/static/generated/{filename}"
            
            print("HF Video: Maximum retries reached for loading model.")
            return None

        except Exception as e:
            print(f"Error in HuggingFace video generation: {e}")
            try:
                if hasattr(e, 'response') and e.response is not None:
                    print(f"HF API Error: {e.response.text}")
            except:
                pass
            return None

