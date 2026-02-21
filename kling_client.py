import requests
import time
import os
import jwt
import logging

logger = logging.getLogger(__name__)

class KlingClient:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api-singapore.klingai.com"

    def _generate_token(self):
        """Generates a JWT token for Kling AI API authentication."""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 3600,  # Token valid for 1 hour
            "nbf": int(time.time()) - 5
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)
        return token

    def generate_video(self, prompt, image_url=None):
        """
        Generates a video from a text prompt or image + prompt using Kling AI.
        """
        if not self.access_key or not self.secret_key:
            raise Exception("Kling AI: Access Key or Secret Key missing")

        token = self._generate_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Use the Omni Video endpoint which handles both T2V and I2V
        endpoint = f"{self.base_url}/v1/videos/omni-video"
        
        payload = {
            "model_name": "kling-v1-6",  # Correct model name is kling-v1-6
            "prompt": prompt,
            "mode": "pro",
            "aspect_ratio": "16:9",
            "duration": "5"
        }

        if image_url:
            payload["image_list"] = [
                {
                    "image_url": image_url,
                    "type": "first_frame"
                }
            ]

        try:
            logger.info(f"Starting Kling AI video generation for: {prompt}")
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code >= 400:
                err_msg = f"Kling API Error {response.status_code}: {response.text[:200]}"
                logger.error(err_msg)
                raise Exception(err_msg)

            data = response.json()
            task_id = data.get("data", {}).get("task_id")
            
            if not task_id:
                err_msg = f"Kling Error: No task ID returned. Response: {data}"
                logger.error(err_msg)
                raise Exception(err_msg)

            logger.info(f"Kling task created with ID: {task_id}")

            # Step 2: Poll for completion
            max_retries = 90  # 15 minutes max (10s * 90)
            retries = 0
            while retries < max_retries:
                status_url = f"{self.base_url}/v1/videos/omni-video/{task_id}"
                try:
                    status_response = requests.get(status_url, headers=headers, timeout=15)
                    if status_response.status_code >= 400:
                        logger.warning(f"Kling Poll Error: {status_response.status_code}")
                        retries += 1
                        time.sleep(10)
                        continue
                except Exception as e:
                    logger.warning(f"Kling Poll Exception: {e}")
                    retries += 1
                    time.sleep(10)
                    continue

                status_data = status_response.json()
                task_info = status_data.get("data", {})
                task_status = task_info.get("task_status", "").upper()
                
                logger.info(f"Kling Task {task_id} status: {task_status}")

                if task_status in ["COMPLETED", "SUCCESS", "SUCCEEDED"]:
                    video_info = task_info.get("video_result", {})
                    # For v1.6, result might be in a different field or list
                    video_url = video_info.get("url")
                    
                    if not video_url:
                        # Check if it's in a list
                        videos = task_info.get("task_result", {}).get("videos", [])
                        if videos:
                            video_url = videos[0].get("url")
                    
                    if video_url:
                        return video_url
                        
                    raise Exception("Kling: Task completed but no URL found in response")
                
                if task_status in ["FAILED", "ERROR", "CANCELLED"]:
                    err_detail = task_info.get('task_status_msg') or "Unknown error"
                    raise Exception(f"Kling Task {task_id} failed: {err_detail}")
                
                retries += 1
                time.sleep(10)
            
            raise Exception(f"Kling generation timed out for task {task_id}")

        except Exception as e:
            logger.error(f"Error in Kling generation: {e}")
            raise e
