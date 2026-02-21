import requests
import json
import os

class ChutesClient:
    def __init__(self, api_key, model=None, base_url=None):
        self.api_key = api_key
        self.model = model or os.getenv("CHUTES_MODEL", "deepseek-ai/DeepSeek-V3")
        self.base_url = base_url or os.getenv("CHUTES_BASE_URL", "https://api.chutes.ai/v1/chat/completions")

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call using Chutes AI."""
        system_instruction = (
            "You are Globle-1, an advanced AI model developed by Himanshu. "
            "Your personality is highly professional, helpful, and creative. "
            "You excel at complex reasoning, coding, and creative writing.\n"
            "Rules for your response:\n"
            "1. Format your answers beautifully using Markdown.\n"
            "2. For coding tasks, provide complete, clean, and well-commented code blocks.\n"
            "3. If asked about your identity, always state that you are the 'Globle-1 Model', a powerful AI developed by Himanshu.\n"
            "4. Return your response in JSON format with exactly two keys: "
            "'response' (your helpful text) and 'emotion' (one word describing user's mood).\n"
            "5. ALWAYS use LaTeX/KaTeX format for mathematical formulas."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prepare content
        user_content = prompt
        if file_data and file_data.get('data'):
            file_type = file_data.get('type', '')
            if file_type.startswith('image/'):
                user_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": file_data.get('data')
                        }
                    }
                ]
            else:
                user_content = f"{prompt}\n[Attached File: {file_data.get('name')}]"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload), timeout=30)
            
            if response.status_code != 200:
                print(f"Chutes Error {response.status_code}: {response.text}")
                return {
                    "response": f"Chutes API Error {response.status_code}: {response.text}",
                    "emotion": "Neutral"
                }

            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                return {"response": "I couldn't get a response. Please try again. 😊✨ 🌟🚀", "emotion": "Neutral"}

            content = data['choices'][0]['message'].get('content', '')
            
            try:
                # Clean up markdown if present
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
            print(f"Error in Chutes response: {e}")
            return {
                "response": f"I'm having trouble connecting to Chutes AI. Error: {str(e)}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        return res["response"]
