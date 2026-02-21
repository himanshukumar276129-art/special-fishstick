import requests
import json
import os

class OllamaClient:
    def __init__(self, api_key, model=None, base_url=None):
        self.api_key = api_key
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-v3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api/chat")

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call using Ollama Global."""
        system_instruction = (
            "You are Globle-1, an advanced AI model developed by Himanshu. "
            "Your personality is highly professional, helpful, and creative. "
            "Rules for your response:\n"
            "1. Format your answers beautifully using Markdown.\n"
            "2. Return your response in JSON format with exactly two keys: "
            "'response' (your helpful text) and 'emotion' (one word describing user's mood).\n"
            "3. If asked about your identity, always state that you are the 'Globle-1 Model', a powerful AI developed by Himanshu."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prepare messages
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"Ollama Error {response.status_code}: {response.text}")
                return {
                    "response": f"Ollama API Error {response.status_code}: {response.text}",
                    "emotion": "Neutral"
                }

            data = response.json()
            content = data.get('message', {}).get('content', '')
            
            try:
                # Robust JSON parsing
                clean_content = content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:-3].strip()
                elif clean_content.startswith("```"):
                    clean_content = clean_content[3:-3].strip()
                
                parsed_data = json.loads(clean_content)
                return {
                    "response": parsed_data.get("response", content),
                    "emotion": parsed_data.get("emotion", "Neutral")
                }
            except json.JSONDecodeError:
                return {
                    "response": content,
                    "emotion": "Neutral"
                }
                
        except Exception as e:
            print(f"Error in Ollama response: {e}")
            return {
                "response": f"I'm having trouble connecting to Ollama. Error: {str(e)}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        return res["response"]
