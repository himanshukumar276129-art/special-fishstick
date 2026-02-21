import requests
import os

class NewsService:
    def __init__(self, api_key=None):
        self.api_key = (api_key or os.getenv("NEWS_API_KEY", "")).strip()
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def get_top_news(self, category="general", country="us"):
        if not self.api_key or self.api_key == "YOUR_NEWS_API_KEY":
            return "News API key is not configured. Please add your News API key to the .env file."
        
        try:
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": 5
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                articles = data.get("articles", [])
                if not articles:
                    return "I couldn't find any news articles at the moment."
                
                news_text = "Here are the top headlines:\n\n"
                for i, article in enumerate(articles, 1):
                    news_text += f"{i}. **{article['title']}**\n"
                    news_text += f"   Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                    if article.get('description'):
                        news_text += f"   _{article['description']}_\n"
                    news_text += "\n"
                
                return news_text
            else:
                return f"Could not fetch news. Error: {data.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Error fetching news: {str(e)}"
