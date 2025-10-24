"""
Cryptocurrency price data fetching module using Binance API
"""

import requests
from typing import Dict, List, Optional
import time
from datetime import datetime


class CryptoAPI:
    """Fetches real-time cryptocurrency prices from Binance"""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.last_prices = {}
        
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a trading pair
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current price or None if error
        """
        try:
            url = f"{self.BASE_URL}/ticker/price"
            params = {'symbol': symbol}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            price = float(data['price'])
            self.last_prices[symbol] = price
            return price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple trading pairs
        
        Args:
            symbols: List of trading pair symbols
            
        Returns:
            Dictionary mapping symbols to prices
        """
        try:
            url = f"{self.BASE_URL}/ticker/price"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for item in data:
                if item['symbol'] in symbols:
                    prices[item['symbol']] = float(item['price'])
                    self.last_prices[item['symbol']] = float(item['price'])
            
            return prices
        except Exception as e:
            print(f"Error fetching multiple prices: {e}")
            return {}
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List[Dict]:
        """
        Get candlestick/kline data for technical analysis
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of klines to fetch
            
        Returns:
            List of kline data dictionaries
        """
        try:
            url = f"{self.BASE_URL}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            klines = []
            for k in data:
                klines.append({
                    'timestamp': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                })
            
            return klines
        except Exception as e:
            print(f"Error fetching klines for {symbol}: {e}")
            return []
    
    def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """
        Get 24-hour statistics for a trading pair
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with 24h statistics
        """
        try:
            url = f"{self.BASE_URL}/ticker/24hr"
            params = {'symbol': symbol}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'symbol': data['symbol'],
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
            }
        except Exception as e:
            print(f"Error fetching 24h stats for {symbol}: {e}")
            return None


if __name__ == "__main__":
    # Test the API
    api = CryptoAPI()
    
    print("Testing single price fetch:")
    btc_price = api.get_price('BTCUSDT')
    print(f"BTC Price: ${btc_price:,.2f}")
    
    print("\nTesting multiple prices fetch:")
    prices = api.get_multiple_prices(['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
    for symbol, price in prices.items():
        print(f"{symbol}: ${price:,.2f}")
    
    print("\nTesting 24h stats:")
    stats = api.get_24h_stats('BTCUSDT')
    if stats:
        print(f"24h Change: {stats['price_change_percent']:.2f}%")
        print(f"24h High: ${stats['high']:,.2f}")
        print(f"24h Low: ${stats['low']:,.2f}")

