import requests
import time
import os

class VeoClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        self.model = model or "veo3"
        self.base_url = "https://veo3api.com"

    def generate_video(self, prompt, image_url=None):
        """
        Generates a video from a text prompt or image + prompt using veo3api.com.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "aspect_ratio": "16:9"
        }

        if image_url:
            payload["image_urls"] = [image_url]

        try:
            print(f"Starting Veo video generation for: {prompt} using model: {self.model}")
            
            # Use the correct endpoint found in official docs
            endpoint = f"{self.base_url}/generate"
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code >= 400:
                err_msg = f"Veo API Error {response.status_code}: {response.text[:200]}"
                print(err_msg)
                # Raise an exception so app.py can catch the specific error
                raise Exception(err_msg)

            data = response.json()
            
            res_data = data.get("data", {}) if isinstance(data.get("data"), dict) else data
            task_id = res_data.get("task_id") or data.get("task_id") or data.get("id")
            
            if not task_id:
                err_msg = f"Veo Error: No task ID returned. Response: {data}"
                print(err_msg)
                raise Exception(err_msg)

            print(f"Veo task created with ID: {task_id}")

            # Step 2: Poll for completion using /feed endpoint
            max_retries = 60 # 10 minutes max (10s * 60)
            retries = 0
            while retries < max_retries:
                status_url = f"{self.base_url}/feed?task_id={task_id}"
                try:
                    status_response = requests.get(status_url, headers=headers, timeout=15)
                    if status_response.status_code >= 400: 
                        print(f"Veo Poll Error: {status_response.status_code}")
                        retries += 1
                        time.sleep(10)
                        continue
                except Exception as e:
                    print(f"Veo Poll Exception: {e}")
                    retries += 1
                    time.sleep(10)
                    continue

                status_data = status_response.json()
                
                # Check nested or top-level status
                res_data = status_data.get("data", {}) if isinstance(status_data.get("data"), dict) else status_data
                status = str(res_data.get("status", status_data.get("status", ""))).upper()
                
                print(f"Veo Task {task_id} status: {status}")

                if status in ["COMPLETED", "SUCCEEDED", "SUCCESS"]:
                    # Try all possible video URL locations
                    res_list = res_data.get("response", status_data.get("response", []))
                    if isinstance(res_list, list) and len(res_list) > 0:
                        return res_list[0]
                    
                    assets = res_data.get("assets", status_data.get("assets", []))
                    if isinstance(assets, list) and len(assets) > 0:
                        asset = assets[0]
                        if isinstance(asset, dict):
                            return asset.get("url") or asset.get("link")
                        return asset
                        
                    url = res_data.get("video_url") or res_data.get("output_url") or \
                           status_data.get("video_url") or status_data.get("output_url") or \
                           res_data.get("url")
                    
                    if url: return url
                    raise Exception("Veo: Task completed but no URL found in response")
                
                if status == "FAILED" or status == "ERROR":
                    err_detail = res_data.get('error') or res_data.get('message') or status_data.get('error')
                    raise Exception(f"Veo Task {task_id} failed: {err_detail}")
                
                retries += 1
                time.sleep(10)
            
            raise Exception(f"Veo generation timed out for task {task_id}")

        except Exception as e:
            print(f"Error in Veo generation: {e}")
            raise e # Reraise to capture in app.py diagnostics
