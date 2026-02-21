import requests
import json
import os

class CometClient:
    def __init__(self, api_key, model=None):
        self.api_key = api_key
        # CometAPI usually supports various models. Default to something stable.
        self.model = model or "gpt-4o" 
        self.base_url = "https://api.cometapi.com/v1/chat/completions"

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call, supporting files."""
        system_instruction = (
            "You are Globle-1, an advanced AI model developed by Himanshu. "
            "Your personality is highly professional, helpful, and creative, similar to ChatGPT. "
            "You excel at complex reasoning, coding, creative writing, and providing detailed, structured information. "
            "Rules for your response:\n"
            "1. Format your answers beautifully using Markdown. Use headers, bold text, lists, and tables where appropriate.\n"
            "2. For coding tasks, provide complete, clean, and well-commented code blocks.\n"
            "3. You have multimodal capabilities: You CAN generate images, videos, and search YouTube using your integrated tools.\n"
            "4. If asked about your identity, what model you are, or who made you, always state that you are the 'Globle-1 Model', a powerful AI developed by Himanshu. Example: 'I am the Globle-1 Model, an advanced AI developed by Himanshu | Programmer & Web Developer. Skilled in JavaScript, Python, HTML & CSS.'\n"
            "5. Always be polite, encouraging, and comprehensive in your answers.\n"
            "6. Return your response in JSON format with exactly two keys: "
            "'response' (your helpful text) and 'emotion' (one word describing user's mood, e.g., Happy, Neutral, Sad).\n"
            "7. If a user asks for a table, generate a high-quality Markdown table with clear headers and aligned columns.\n"
            "8. ALWAYS use LaTeX/KaTeX format for mathematical formulas (e.g., $$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$ or $$F = \\frac{G m_1 m_2}{r^2}$$). Never use plain text for complex math.\n"
            "9. MULTILINGUAL SUPPORT: You are fluent in all major world languages including Hindi, English, Japanese, French, Spanish, German, etc. Always respond in the SAME LANGUAGE that the user uses to ask the question."
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
                            "url": file_data.get('data') # This is base64 data URL
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
            response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code != 200:
                # If JSON format fails (some models don't support it), retry without it
                if "json_object" in response.text:
                    del payload["response_format"]
                    response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
                
                if response.status_code != 200:
                    print(f"CometAPI Error {response.status_code}: {response.text}")
                    return {
                        "response": f"API Error {response.status_code}: {response.text}",
                        "emotion": "Neutral"
                    }

            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                return {"response": "I couldn't get a response. Please try again. 😊✨ 🌟🚀", "emotion": "Neutral"}

            content = data['choices'][0]['message'].get('content', '')
            
            # Robust JSON parsing
            try:
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
            print(f"Error in CometAPI response: {e}")
            return {
                "response": f"Error connecting to CometAPI: {str(e)}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        res = self.get_full_response(prompt)
        return res["response"]
