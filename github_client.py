import requests
import logging
import os

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://models.inference.ai.azure.com"
        # Use GITHUB_MODEL from environment if available
        self.model = os.getenv("GITHUB_MODEL", "gpt-4o") 

    def get_full_response(self, prompt, file_data=None):
        """
        Generates text response using GitHub Models (Azure AI Inference).
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format payload
        import json
        
        content_text = prompt
        # Note: GitHub/Azure models might support multi-modal input differently, 
        # but for now we'll append file info to text if present.
        if file_data and file_data.get('isText'):
             content_text += f"\n\n[Attached File Content]:\n{file_data.get('data')}"
        elif file_data:
             content_text += f"\n\n[Attached File: {file_data.get('name')}] (File processing limited)"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": (
                        "You are Globle-1, an advanced AI model developed by Himanshu. "
                        "Your personality is highly professional, helpful, and creative, similar to ChatGPT. "
                        "You excel at complex reasoning, coding, creative writing, and providing detailed, structured information. "
                        "Rules for your response:\n"
                        "1. Format your answers beautifully using Markdown. Use headers, bold text, lists, and tables where appropriate.\n"
                        "2. For coding tasks, provide complete, clean, and well-commented code blocks.\n"
                        "3. If asked about your identity, what model you are, or who made you, always state that you are the 'Globle-1 Model', a powerful AI developed by Himanshu. Example: 'I am the Globle-1 Model, an advanced AI developed by Himanshu | Programmer & Web Developer.'\n"
                        "4. Return your response in JSON format with exactly two keys: "
                        "'response' (your helpful text) and 'emotion' (one word describing user's mood, e.g., Happy, Neutral, Sad).\n"
                        "5. ALWAYS use LaTeX/KaTeX format for mathematical formulas."
                    )
                },
                {"role": "user", "content": content_text}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            # Use specific chat completion endpoint
            endpoint = f"{self.base_url}/chat/completions"
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            try:
                json_content = json.loads(content)
                return {
                    "response": json_content.get("response", content),
                    "emotion": json_content.get("emotion", "Neutral")
                }
            except:
                return {"response": content, "emotion": "Neutral"}

        except Exception as e:
            logger.error(f"GitHub Models Text Error: {e}")
            return None

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        if res: return res.get("response")
        return None

    def generate_video(self, prompt, image_url=None):
        """
        Attempt to generate video using GitHub Models.
        Note: Currently GitHub Models (Azure AI Inference) primarily supports text/chat/embeddings.
        This generic implementation checks for video capabilities but will likely return a disclaimer.
        """
        try:
            logger.info(f"GitHub Models: Received video request for '{prompt[:30]}...'")
            
            # Since there is no public standard video generation endpoint for GitHub Models yet,
            # we will return None with a specific log message. 
            # If a specific endpoint becomes available, it should be added here.
            
            logger.warning("GitHub Models currently supports LLMs (Text/Chat). Video generation is not natively supported via this token yet.")
            return None
            
        except Exception as e:
            logger.error(f"GitHub Models Error: {e}")
            return None
