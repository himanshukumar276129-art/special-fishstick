import requests
import os
import random
import logging
import re

logger = logging.getLogger(__name__)

class EmojiService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://emoji-api.com"
        # Cache for basic emotions - removed neutral faces in favor of happy ones
        self.emotion_cache = {
            "Happy": "😊✨",
            "Sad": "😔💧",
            "Angry": "😠🔥",
            "Surprised": "😮🌟",
            "Neutral": "😊✨", # Default neutral to happy as requested
            "Thinking": "🤔💭"
        }
        # Common keywords and their emojis (Massively expanded)
        self.keyword_map = {
            # Core & System
            "weather": "🌦️", "sun": "☀️", "rain": "🌧️", "cloud": "☁️", "thunder": "⚡", "snow": "❄️",
            "news": "📰", "breaking": "🚨", "world": "🌍", "india": "🇮🇳", "tech": "💻", "science": "🧬",
            "search": "🔍", "find": "🔎", "youtube": "📺", "video": "🎥", "music": "🎵", "song": "🎶",
            "time": "⏰", "date": "📅", "location": "📍", "map": "🗾", "clock": "🕒",
            
            # Finance & Pro
            "price": "💰", "money": "💸", "crypto": "🪙", "bitcoin": "₿", "stock": "📈", "market": "📊",
            "pro": "🏆", "premium": "⭐", "gold": "🟡", "success": "✅", "done": "✔️", "error": "❌",
            "buy": "🛒", "sell": "📉", "earn": "💹", "recharge": "🔋", "free": "🆓",
            
            # People & Professions
            "people": "👥", "man": "👨", "woman": "👩", "person": "👤", "friend": "🤝", "group": "👬",
            "actor": "🎭", "singer": "🎤", "doctor": "👨‍⚕️", "teacher": "👨‍🏫", "hero": "🦸",
            "leader": "👑", "president": "🏛️", "king": "👑", "queen": "👸", "star": "⭐", "developer": "👨‍💻",
            
            # Media & Creative
            "image": "🖼️", "photo": "📸", "draw": "🎨", "art": "🎭", "design": "📐", "book": "📚",
            "game": "🎮", "play": "🕹️", "movie": "🎬", "camera": "📹", "flash": "📸",
            
            # Social & Emotion
            "hello": "👋", "hi": "✨", "help": "🆘", "thanks": "🙏", "welcome": "🎉", "cool": "😎",
            "amazing": "🤩", "love": "❤️", "heart": "💖", "fun": "💃", "celebrate": "🎊", "party": "🥳",
            "idea": "💡", "think": "🤔", "smart": "🧠", "beautiful": "🌺", "nice": "👍", "great": "💪",
            "fast": "⚡", "quick": "🏃", "easy": "✨", "hard": "🧱", "fire": "🔥", "rocket": "🚀", "point": "👉",
            "yes": "✅", "no": "❌", "stop": "🛑", "go": "🟢", "danger": "⚠️", "warning": "⚡", "win": "🏆",
            "lose": "📉", "sport": "⚽", "cricket": "🏏", "food": "🍕", "water": "💧", "drink": "🥤",
            "apple": "🍎", "fruit": "🍓", "cat": "🐱", "dog": "🐶", "bird": "🐦", "nature": "🌲",
            "home": "🏠", "school": "🏫", "office": "🏢", "car": "🚗", "plane": "✈️", "ship": "🚢",
            "phone": "📱", "laptop": "💻", "watch": "⌚", "battery": "🔋", "signal": "📶", "wifi": "📡",
            "angry": "🗯️", "sleepy": "😴", "cool": "😎", "smile": "😊", "laugh": "😂", "cry": "😢",
            "shock": "😱", "fear": "😨", "proud": "😌", "luck": "🍀", "gift": "🎁", "cake": "🎂",
            "right": "✅", "wrong": "❌", "true": "✅", "false": "❌", "correct": "✅", "incorrect": "❌"
        }

    def get_emoji_by_keyword(self, keyword):
        """Fetch an emoji based on a keyword from emoji-api.com or map"""
        keyword = keyword.lower().strip()
        
        # Check local map first
        if keyword in self.keyword_map:
            return self.keyword_map[keyword]
            
        if not self.api_key:
            return ""
            
        try:
            url = f"{self.base_url}/emojis?search={keyword}&access_key={self.api_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                emojis = response.json()
                if emojis and isinstance(emojis, list):
                    return random.choice(emojis).get('character', "")
        except Exception as e:
            logger.error(f"Error fetching emoji for keyword {keyword}: {e}")
        
        return ""

    def get_emoji_for_emotion(self, emotion):
        """Get a relevant emoji from the API or cache. Neutral is treated as Happy."""
        search_emotion = emotion
        if emotion == "Neutral":
            search_emotion = "Happy" # Force happy emojis for neutral states
            
        if not self.api_key:
            return self.emotion_cache.get(search_emotion, "😊✨")

        emoji = self.get_emoji_by_keyword(search_emotion.lower())
        # Block boring neutral face if API returns it
        if not emoji or emoji == "😊":
            return self.emotion_cache.get(search_emotion, "😊✨")
            
        return emoji

    def augment_text_with_emojis(self, text, emotion="Neutral"):
        """Add emojis within and at the end of the text to make it more attractive"""
        if not text:
            return text
            
        augmented_text = text
        
        # 1. Inject emojis after key words (Increase to 5 injections for "all time" emoji feel)
        words_found = []
        # Sort keys by length descending to match longer keywords first (e.g., "recharge" before "charge")
        sorted_keys = sorted(self.keyword_map.keys(), key=len, reverse=True)
        
        for word in sorted_keys:
            if len(words_found) >= 5:
                break
            emoji = self.keyword_map[word]
            if re.search(r'\b' + re.escape(word) + r'\b', augmented_text.lower()):
                # Ensure we don't inject the neutral face
                if emoji not in augmented_text and emoji != "😊":
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    augmented_text = pattern.sub(f"{word} {emoji}", augmented_text, count=1)
                    words_found.append(word)

        # 2. Add number emojis (1-9) to list items or mentions
        number_map = {
            "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣",
            "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "10": "🔟"
        }
        for num, emoji in number_map.items():
            # Replace digit followed by a dot (like "1.") or standalone digits
            pattern = re.compile(r'\b' + num + r'\.', re.IGNORECASE)
            augmented_text = pattern.sub(f"{emoji}.", augmented_text)
        
        # 3. Add emotion emojis at the end (Always add at least 2)
        emotion_emoji = self.get_emoji_for_emotion(emotion)
        
        # 3. Add random "flair" emojis (Always add 2-3 random ones to make it very attractive)
        flairs = ["✨", "🌟", "🔥", "🚀", "💎", "⚡", "🌈", "💠", "🎊", "🎉", "🔥"]
        random_flairs = "".join(random.sample(flairs, 2))
            
        return f"{augmented_text} {emotion_emoji} {random_flairs}".strip()

# Initialize from environment
EMOJI_API_KEY = os.getenv("EMOJI_API_KEY")
emoji_service = EmojiService(EMOJI_API_KEY)
