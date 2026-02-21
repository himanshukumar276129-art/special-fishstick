import requests
import time
import logging

logger = logging.getLogger(__name__)

class ReplicateClient:
    def __init__(self, api_token, model="minimax/video-01"):
        """
        Initialize the Replicate Client.
        :param api_token: The Replicate API Token
        :param model: The model identifier (e.g., 'minimax/video-01' or 'stability-ai/stable-video-diffusion:...')
                      If a version hash is provided in the model string (after colon), predictions endpoint is used differently or via version.
                      Here we assume the user provides owner/name and we rely on the latest version unless specified.
                      For 'minimax/video-01', we can use the models endpoint.
        """
        self.api_token = api_token
        self.model = model
        self.base_url = "https://api.replicate.com/v1"

    def generate_video(self, prompt, image_url=None):
        """
        Generate a video using Replicate API.
        """
        if not self.api_token:
            raise Exception("Replicate API Token is missing")
        
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            #"Prefer": "wait" # Wait a bit for short tasks, but video usually takes longer
        }

        # Prepare input based on common video model schemas
        # Minimax Video-01: 'prompt' (required), 'first_frame_image' (optional)
        input_data = {
            "prompt": prompt
        }
        
        if image_url:
            # Different models might name this differently.
            # Minimax: 'first_frame_image'
            # Stable Video Diffusion: 'input_image'
            # AnimateDiff: usually just prompt, no image
            
            if "minimax" in self.model:
                input_data["first_frame_image"] = image_url
            elif "stable-video" in self.model or "svd" in self.model:
                input_data["input_image"] = image_url
            else:
                # Fallback generic key, or ignore (since prompt is main)
                # But let's try 'input_image' as a common second guess or 'image'
                input_data["first_frame_image"] = image_url

        # Check if model has a version hash (e.g. owner/name:hash)
        if ":" in self.model:
            # It's a version
            version_id = self.model.split(":")[1]
            url = f"{self.base_url}/predictions"
            payload = {
                "version": version_id,
                "input": input_data
            }
        else:
            # It's a model path, assume latest version
            url = f"{self.base_url}/models/{self.model}/predictions"
            payload = {
                "input": input_data
            }
            
        try:
            logger.info(f"Replicate: Starting generation with model {self.model}")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code >= 400:
                logger.error(f"Replicate API Error: {response.text}")
                raise Exception(f"Replicate Error {response.status_code}: {response.text}")

            data = response.json()
            
            prediction_id = data.get("id")
            if not prediction_id:
                 raise Exception(f"No prediction ID returned: {data}")
                 
            logger.info(f"Replicate prediction created: {prediction_id}")
            
            # Poll for completion
            status = data.get("status")
            max_retries = 120 # 10 minutes (5s interval)
            retries = 0
            
            while status not in ["succeeded", "failed", "canceled"] and retries < max_retries:
                time.sleep(5)
                resp = requests.get(f"{self.base_url}/predictions/{prediction_id}", headers=headers)
                
                if resp.status_code >= 400:
                    logger.warning(f"Replicate Poll Error: {resp.status_code}")
                    retries += 1
                    continue
                    
                data = resp.json()
                status = data.get("status")
                logger.info(f"Replicate status for {prediction_id}: {status}")
                retries += 1

            if status == "succeeded":
                output = data.get("output")
                # Output can be a string (url) or list of strings
                if isinstance(output, list) and len(output) > 0:
                    return output[0]
                elif isinstance(output, str):
                    return output
                else:
                    raise Exception(f"Unexpected output format: {output}")
            elif status == "failed":
                raise Exception(f"Replicate generation failed: {data.get('error')}")
            elif status == "canceled":
                raise Exception("Replicate generation canceled")
            else:
                raise Exception("Replicate generation timed out")

        except Exception as e:
            logger.error(f"Replicate Client Error: {e}")
            raise e
