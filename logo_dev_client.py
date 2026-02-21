import requests
import logging

logger = logging.getLogger(__name__)

class LogoDevClient:
    def __init__(self, key_pairs, secret_key=None):
        """
        key_pairs: list of dicts like [{"pk": "...", "sk": "..."}], or a single PK string
        secret_key: optional SK string (if key_pairs is a PK string)
        """
        if isinstance(key_pairs, str) and secret_key:
            self.key_pairs = [{"pk": key_pairs, "sk": secret_key}]
        elif isinstance(key_pairs, dict):
            self.key_pairs = [key_pairs]
        else:
            self.key_pairs = [kp for kp in key_pairs if kp.get("pk")]
            
        self.base_url = "https://img.logo.dev/"

    def generate_image(self, prompt):
        """
        Attempts to fetch a professional logo from Logo.dev library.
        Tries all available API key pairs.
        """
        if not self.key_pairs:
            logger.error("Logo.dev API keys are missing.")
            return None

        # Clean prompt to get potential brand name or domain
        clean_text = prompt.lower()
        for word in ["generate", "create", "make", "logo for", "logo of", "a logo", "the logo", "professional logo", "logo.dev"]:
            clean_text = clean_text.replace(word, "")
        
        identifier = clean_text.strip()
        
        if not identifier:
            logger.warning("Logo.dev received empty identifier after cleaning.")
            return None

        variations = [identifier]
        if " " not in identifier and "." not in identifier:
            variations.append(f"{identifier}.com")
            variations.append(f"{identifier}.org")
            variations.append(f"{identifier}.net")

        for key_pair in self.key_pairs:
            pk = key_pair.get("pk")
            try:
                for brand_id in variations:
                    # Use GET for better compatibility with CDNs
                    url = f"https://img.logo.dev/{brand_id}?token={pk}&size=256"
                    
                    logger.info(f"🔍 Logo.dev searching for: {brand_id} with key {pk[:10]}...")
                    
                    # We use GET with a stream=True to avoid downloading the whole image just to check existence
                    response = requests.get(url, timeout=5, stream=True)
                    if response.status_code == 200:
                        logger.info(f"✓ Logo.dev found logo for: {brand_id}")
                        return url
                    
                    # Log failure details for debugging
                    logger.warning(f"✗ Logo.dev {brand_id} returned {response.status_code} with key {pk[:10]}")
                
            except Exception as e:
                logger.error(f"✗ Logo.dev key pair {pk[:10]} error: {e}")
                continue 

        return None
