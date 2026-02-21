import requests
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class PollinationsClient:
    def __init__(self, api_keys):
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = [k for k in api_keys if k]
        self.base_url = "https://pollinations.ai/p/"

    def generate_image(self, prompt_text):
        """
        Generates an image/logo using Pollinations.ai.
        """
        if not self.api_keys:
            logger.error("Pollinations API keys are missing.")
            return None

        # Clean and enhance prompt for logo generation
        if "logo" not in prompt_text.lower():
            enhanced_prompt = f"professional minimalist logo for {prompt_text}, high resolution, vector style, white background"
        else:
            enhanced_prompt = prompt_text

        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        
        for api_key in self.api_keys:
            # Pollinations CDN URL format
            # We add parameters for better quality and no logo overlap
            url = f"https://pollinations.ai/p/{encoded_prompt}?nologo=true&enhance=false&width=1024&height=1024"
            
            try:
                # We verify if we can reach it
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                logger.info(f"🎨 Pollinations generating logo for: {enhanced_prompt[:50]}...")
                # We use a GET with a timeout to verify the link
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                
                if response.status_code == 200:
                    logger.info("✓ Pollinations logo generation link verified.")
                    return url
                else:
                    logger.warning(f"✗ Pollinations returned {response.status_code} with key {api_key[:10]}")
                    
            except Exception as e:
                logger.error(f"✗ Pollinations error with key {api_key[:10]}: {e}")
                continue

        return None
