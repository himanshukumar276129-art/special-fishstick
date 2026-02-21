import requests
import os
import json

class BytezClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        # Default to a powerful model available on Bytez
        self.model = model or "bytez/deepseek-v3"
        self.base_url = "https://api.bytez.com/v1/chat/completions"

    def get_full_response(self, prompt, file_data=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Handle file data if text
        content_text = prompt
        if file_data and file_data.get('isText'):
             content_text += f"\n\n[Attached File Content]:\n{file_data.get('data')}"
        elif file_data:
             content_text += f"\n\n[Attached File: {file_data.get('name')}] (File processing not supported on this tier)"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Globle-1, an advanced AI model developed by Himanshu. "
                        "Your personality is highly professional, helpful, and creative, similar to ChatGPT. "
                        "Your goal is to provide accurate, helpful, and beautifully formatted responses. "
                        "Rules for your response:\n"
                        "1. Format your answers beautifully using Markdown.\n"
                        "2. For coding tasks, provide complete, clean, and well-commented code blocks.\n"
                        "3. Return your response in JSON format with exactly two keys: "
                        "'response' (your helpful text) and 'emotion' (one word describing user's mood, e.g., Happy, Neutral, Sad).\n"
                        "4. ALWAYS use LaTeX/KaTeX format for mathematical formulas."
                    )
                },
                {
                    "role": "user",
                    "content": content_text
                }
            ],
            # Some models on Bytez might not support json_object yet, but we'll try it
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
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
            print(f"Bytez Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Bytez Details: {e.response.text}")
            return None

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        if res: return res.get("response")
        return None
