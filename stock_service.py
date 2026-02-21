import requests
import os

class StockService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_stock_price(self, symbol):
        """Fetches the latest price for a given stock symbol (e.g., AAPL, TSLA)."""
        if not self.api_key:
            return "Alpha Vantage API key not configured."

        parameters = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=parameters)
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price = float(quote["05. price"])
                change_percent = quote["10. change percent"]
                return f"The current price of {symbol.upper()} is ${price:,.2f} ({change_percent})."
            else:
                return f"Sorry, I couldn't find stock data for {symbol.upper()}. Please check the symbol."
        except Exception as e:
            print(f"Error fetching stock price: {e}")
            return f"Error fetching stock data for {symbol.upper()}."

    def get_market_news(self, symbol=None):
        """Fetches market news, optionally filtered by symbol."""
        parameters = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key
        }
        if symbol:
            parameters["tickers"] = symbol.upper()

        try:
            response = requests.get(self.base_url, params=parameters)
            response.raise_for_status()
            data = response.json()
            
            if "feed" in data:
                articles = data["feed"][:3]
                news_text = "Latest Stock Market News:\n"
                for article in articles:
                    news_text += f"- {article['title']} ({article['source']})\n"
                return news_text
            else:
                return "No recent market news found."
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return "Error fetching market news."
