from runwayml import RunwayML
import os
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class RunwayClient:
    def __init__(self, api_key):
        self.client = RunwayML(api_key=api_key)

    def generate_video(self, prompt, image_url=None, model="gen3a_turbo"):
        """
        Generates a video from a text prompt or image + prompt.
        """
        try:
            print(f"Starting RunwayML video generation for: {prompt}")
            
            # Ensure prompt is not empty
            prompt = prompt.strip() if prompt else "A cinematic scene"
            if not prompt: prompt = "A cinematic scene"

            if image_url:
                # Image-to-Video
                try:
                    # Gen-3 Alpha Turbo Image-to-Video
                    logger.info(f"RunwayML: Calling Gen-3 Turbo (Image) with prompt: {prompt[:50]}...")
                    # ratio "1280:768" is supported for Gen-3 Alpha Turbo
                    job = self.client.image_to_video.create(
                        model="gen3a_turbo",
                        prompt_image=image_url,
                        prompt_text=prompt,
                        duration=5,
                        ratio="1280:768"
                    )
                except Exception as e:
                    logger.warning(f"RunwayML: Gen-3 Turbo (Image) failed: {e}")
                    # Fallback to Gen-2
                    job = self.client.image_to_video.create(
                        model="gen2",
                        prompt_image=image_url,
                        prompt_text=prompt
                    )
            else:
                # Text-to-Video (Gen-3 Alpha Turbo)
                try:
                    logger.info(f"RunwayML: Calling Gen-3 Turbo (Text) with prompt: {prompt[:50]}...")
                    job = self.client.text_to_video.create(
                        model="gen3a_turbo",
                        prompt_text=prompt,
                        duration=5,
                        ratio="1280:768"
                    )
                except Exception as e:
                    logger.warning(f"RunwayML: Gen-3 Turbo (Text) failed, trying gen2: {e}")
                    # Gen-2 Text-to-Video
                    job = self.client.text_to_video.create(
                        model="gen2",
                        prompt_text=prompt
                    )


            
            task_id = job.id
            print(f"Task created with ID: {task_id}")

            # Poll for completion
            while True:
                task = self.client.tasks.retrieve(task_id)
                status = task.status
                print(f"Task {task_id} status: {status}")

                if status == "SUCCEEDED":
                    output = task.output
                    if isinstance(output, list) and len(output) > 0:
                        return output[0]
                    return output
                elif status == "FAILED":
                    print(f"Task {task_id} failed: {task.error}")
                    return None
                
                # Wait before polling again
                time.sleep(10)
                
        except Exception as e:
            err_msg = f"RunwayML Error: {str(e)}"
            print(err_msg)
            raise Exception(err_msg)

    def get_task_status(self, task_id):
        try:
            task = self.client.tasks.retrieve(task_id)
            return task
        except Exception as e:
            print(f"Error retrieving task: {e}")
            return None
