import os
import requests
from duckduckgo_search import DDGS

class SearchEngineClient:
    def __init__(self):
        self.google_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.tavily_key_2 = os.getenv("TAVILY_API_KEY_2")
        self.tavily_key_3 = os.getenv("TAVILY_API_KEY_3")
        self.tavily_key_4 = os.getenv("TAVILY_API_KEY_4")
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.serper_key_2 = os.getenv("SERPER_API_KEY_2")
        self.ddg_enabled = os.getenv("DUCKDUCKGO_SEARCH_ENABLED", "true").lower() == "true"

    def search(self, query):
        """Unified search with 4-tier fallback."""
        
        # Tier 1: Serper.dev (Google Search API - Fastest & Most Accurate)
        # Supports multiple keys for higher limits
        for s_key in [self.serper_key, self.serper_key_2]:
            if s_key:
                try:
                    headers = {'X-API-KEY': s_key, 'Content-Type': 'application/json'}
                    resp = requests.post(
                        "https://google.serper.dev/search",
                        headers=headers,
                        json={"q": query},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        results = resp.json().get('organic', [])
                        if results:
                            return self._format_results("Serper", results)
                    else:
                        print(f"Serper Search API Warning (Key ending {s_key[-4:]}): Received status {resp.status_code}")
                except Exception as e:
                    print(f"Serper Search Error: {e}")

        # Tier 2: Google Search (Custom Search JSON API)
        if self.google_key and self.google_cx:
            try:
                url = f"https://www.googleapis.com/customsearch/v1?key={self.google_key}&cx={self.google_cx}&q={query}"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    results = resp.json().get('items', [])
                    if results:
                        return self._format_results("Google", results)
                else:
                    print(f"Google Search API Warning: Received status {resp.status_code}")
                    # Optional: Print detailed error for debugging
                    # print(resp.text)
            except Exception as e:
                print(f"Google Search Error: {e}")

        # Tier 3: Tavily (Highly optimized for LLMs)
        for t_key in [self.tavily_key, self.tavily_key_2, self.tavily_key_3, self.tavily_key_4]:
            if t_key:
                try:
                    resp = requests.post(
                        "https://api.tavily.com/search",
                        json={"api_key": t_key, "query": query, "search_depth": "basic"},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        results = resp.json().get('results', [])
                        if results:
                            return self._format_results("Tavily", results)
                except Exception as e:
                    print(f"Tavily Search Error: {e}")

        # Tier 4: DuckDuckGo (Free & Unlimited)
        if self.ddg_enabled:
            try:
                results = []
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=5):
                        results.append(r)
                if results:
                    return self._format_results("DuckDuckGo", results)
            except Exception as e:
                print(f"DuckDuckGo Search Error: {e}")

        return "I couldn't find any search results for that query."

    def _format_results(self, provider, results):
        formatted = f"### Search Results ({provider})\n\n"
        for i, res in enumerate(results[:5], 1):
            title = res.get('title') or res.get('snippet', 'No Title')
            link = res.get('link') or res.get('url', '#')
            snippet = res.get('snippet') or res.get('content', '')
            formatted += f"{i}. **[{title}]({link})**\n   {snippet}\n\n"
        return formatted

search_client = SearchEngineClient()
