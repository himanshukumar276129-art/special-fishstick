import requests
import logging

logger = logging.getLogger(__name__)

class LogoKitClient:
    def __init__(self, api_keys):
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = [k for k in api_keys if k]
        # For LogoKit, we primarily use the direct retrieval or search
        self.base_url = "https://img.logokit.com/"

    def generate_image(self, prompt):
        """
        Attempts to fetch a professional logo from LogoKit library.
        Tries all available API keys.
        """
        if not self.api_keys:
            logger.error("LogoKit API keys are missing.")
            return None

        # Clean prompt to get a potential brand name or domain
        clean_text = prompt.lower()
        for word in ["generate", "create", "make", "logo for", "logo of", "a logo", "the logo", "professional logo"]:
            clean_text = clean_text.replace(word, "")
        
        identifier = clean_text.strip()
        
        if not identifier:
            logger.warning("LogoKit received empty identifier after cleaning.")
            return None

        for api_key in self.api_keys:
            try:
                # Step 1: Try direct name/identifier
                url = f"https://img.logokit.com/{identifier}?token={api_key}&size=256&fallback=404"
                
                logger.info(f"🔍 LogoKit searching for: {identifier} with key {api_key[:8]}...")
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✓ LogoKit found logo for: {identifier}")
                    return url
                
                # Step 2: If it's a single word and no dot, try adding .com
                if " " not in identifier and "." not in identifier:
                    domain_identifier = f"{identifier}.com"
                    url = f"https://img.logokit.com/{domain_identifier}?token={api_key}&size=256&fallback=404"
                    
                    logger.info(f"🔍 LogoKit searching for: {domain_identifier} with key {api_key[:8]}...")
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✓ LogoKit found logo for: {domain_identifier}")
                        return url

                logger.info(f"✗ LogoKit could not find logo for: {identifier} with key {api_key[:8]}")
            except Exception as e:
                logger.error(f"✗ LogoKit key {api_key[:8]} error: {e}")
                continue # Try next key

        return None
