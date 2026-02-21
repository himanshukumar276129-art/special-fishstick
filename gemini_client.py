import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self, api_key):
        if api_key:
            api_key = api_key.strip()
        genai.configure(api_key=api_key)
        
        self.model = None
        self._configure_model()

    def _configure_model(self):
        """Dynamically find a working model availability."""
        try:
            print("Searching for available Gemini models...")
            # List all models available to this API key
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            print(f"Found models: {available_models}")

            # clear model names (remove 'models/' prefix if present)
            clean_models = [m.replace('models/', '') for m in available_models]

            # Priority list - Updated to use current available models
            priorities = [
                'gemini-2.5-flash', 'gemini-2.5-pro',
                'gemini-2.0-flash', 'gemini-flash-latest',
                'gemini-flash-lite-latest', 'gemini-pro-latest',
                'gemini-2.5-flash-lite', 'gemini-2.0-flash-lite'
            ]
            
            selected_model_name = None
            
            # Check for priority match
            for p in priorities:
                # Check for exact match OR 'models/' prefix match
                if p in clean_models:
                    selected_model_name = p
                    break
                # Check if it exists with 'models/' in the original list
                for full_m in available_models:
                    if p in full_m:
                        selected_model_name = full_m
                        break
                if selected_model_name:
                    break
            
            # Fallback to first available if no priority match
            if not selected_model_name and clean_models:
                selected_model_name = available_models[0]

            if selected_model_name:
                print(f"Selected model: {selected_model_name}")
                self.model = genai.GenerativeModel(selected_model_name)
            else:
                print("CRITICAL: No text generation models found for this API Key.")
                
        except Exception as e:
            print(f"Error configuring models: {e}")

    def get_full_response(self, prompt, file_data=None):
        """Generates response and emotion in a single call, supporting optional file attachments."""
        if not self.model:
            self._configure_model()
            if not self.model:
                return {"response": "Error: No AI model available.", "emotion": "Neutral"}

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
            "9. MULTILINGUAL SUPPORT: You are fluent in all major world languages including Hindi, English, Japanese, French, Spanish, German, etc. Always respond in the SAME LANGUAGE that the user uses to ask the question.\n"
            "10. IMPORTANT: DO NOT attempt to generate images or videos yourslf using text. If a user asks for an image or video, your internal tools will handle it BEFORE it reaches you. If you are reading this, it means the tools were skipped; simply reply 'I am unable to generate that specific media right now.'"
        )
        
        try:
            content_parts = [f"{system_instruction}\n\nUser: {prompt}"]
            
            if file_data and file_data.get('data'):
                file_type = file_data.get('type', '')
                
                if file_data.get('isText'):
                    # It's a text file, append content as context
                    content_parts[0] += f"\n\n[Context from attached file '{file_data.get('name')}']:\n{file_data.get('data')}"
                elif file_type.startswith('image/'):
                    # It's an image, decode base64
                    base64_data = file_data.get('data').split(',')[-1]
                    import base64
                    image_bytes = base64.b64decode(base64_data)
                    content_parts.append({
                        "mime_type": file_type,
                        "data": image_bytes
                    })
                else:
                    # Generic fallback
                    content_parts[0] += f"\n[Attached File: {file_data.get('name')}]"

            response = self.model.generate_content(content_parts)
            
            # Simple parsing if AI follows instructions
            text = response.text
            import json
            try:
                # Use regex or simple split to find JSON if AI adds extra text
                if "{" in text and "}" in text:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    data = json.loads(text[start:end])
                    
                    # Be robust: check for 'final' wrapper which some models use
                    if "final" in data and isinstance(data["final"], dict):
                        return {
                            "response": data["final"].get("response", "I'm here to help."),
                            "emotion": data["final"].get("emotion", data.get("emotion", "Neutral"))
                        }
                    
                    return {
                        "response": data.get("response", "I'm here to help."),
                        "emotion": data.get("emotion", "Neutral")
                    }
            except:
                pass
            
            return {"response": text, "emotion": "Neutral"}

        except Exception as e:
            error_str = str(e)
            print(f"Error in Gemini response: {error_str}")
            
            if "429" in error_str:
                return {
                    "response": "⚠️ **Rate Limit Reached**: The free version of Gemini allows only a few requests per minute. Please wait 30 seconds and try again.",
                    "emotion": "Neutral"
                }
            
            if "403" in error_str or "PermissionDenied" in error_str:
                 return {
                    "response": "⚠️ **Access Denied (403)**: The configured Gemini API Key is invalid, expired, or does not have access to the selected model. please check your API key in the .env file.",
                    "emotion": "Sad"
                }
            
            return {
                "response": f"I'm having trouble connecting to my brain. Error: {error_str}",
                "emotion": "Neutral"
            }

    def get_response(self, prompt):
        # Kept for compatibility but recommended to use get_full_response
        res = self.get_full_response(prompt)
        return res["response"]

    def analyze_emotion(self, text):
        # Kept for compatibility but recommended to use get_full_response
        return "Neutral"
