import requests
import os

class CryptoService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    def get_price(self, symbol):
        """Fetches the latest price for a given cryptocurrency symbol (e.g., BTC, ETH)."""
        if not self.api_key:
            return "CoinMarketCap API key not configured."

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        
        parameters = {
            'symbol': symbol.upper(),
            'convert': 'USD'
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=parameters)
            response.raise_for_status()
            data = response.json()
            
            # Navigate the response structure
            crypto_data = data['data'][symbol.upper()]
            name = crypto_data['name']
            price = crypto_data['quote']['USD']['price']
            percent_change_24h = crypto_data['quote']['USD']['percent_change_24h']
            
            return f"The current price of {name} ({symbol.upper()}) is ${price:,.2f}. (24h change: {percent_change_24h:+.2f}%)"
        except Exception as e:
            print(f"Error fetching crypto price: {e}")
            return f"Sorry, I couldn't fetch the price for {symbol}. Make sure the symbol is correct."

    def get_top_cryptos(self, limit=5):
        """Fetches top N cryptocurrencies by market cap."""
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        parameters = {
            'start': '1',
            'limit': str(limit),
            'convert': 'USD'
        }

        try:
            response = requests.get(url, headers=headers, params=parameters)
            response.raise_for_status()
            data = response.json()
            
            top_list = []
            for item in data['data']:
                name = item['name']
                symbol = item['symbol']
                price = item['quote']['USD']['price']
                top_list.append(f"{name} ({symbol}): ${price:,.2f}")
            
            return "Top Cryptocurrencies:\n" + "\n".join(top_list)
        except Exception as e:
            print(f"Error fetching top cryptos: {e}")
            return "Sorry, I couldn't fetch the top cryptocurrencies right now."
