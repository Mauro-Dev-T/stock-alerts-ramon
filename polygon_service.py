import requests
from config import POLYGON_API_KEY

BASE_URL = "https://api.polygon.io/v1"


def get_stock_price(symbol):
    """Gets the current price of a stock"""
    try:
        url = f"{BASE_URL}/open-close/{symbol}/2024-01-01"
        params = {"adjusted": "true", "apiKey": POLYGON_API_KEY}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('close', None)
        return None
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None


def get_historical_data(symbol, days=200):
    """It obtains historical data on a stock"""
    try:
        url = f"{BASE_URL}/aggs/ticker/{symbol}/range/1/day/2023-01-01/2024-12-31"
        params = {"apiKey": POLYGON_API_KEY}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            # Return to last 'days' closing prices
            prices = [r['c'] for r in results[-days:]]
            return prices
        return []
    except Exception as e:
        print(f"Error getting historical data for {symbol}: {e}")
        return []


def calculate_sma(prices, period=200):
    """Calculate the simple moving average"""
    if len(prices) < period:
        return None

    sma = sum(prices[-period:]) / period
    return round(sma, 2)


def check_alert_condition(symbol, current_price, sma, threshold=0.01):
    """
    Detects if the price is within the SMA threshold
    Returns: None, 'UP' (bullish), or 'DOWN' (bearish)
    """
    if current_price is None or sma is None:
        return None

    upper_bound = sma * (1 + threshold)
    lower_bound = sma * (1 - threshold)

    if lower_bound <= current_price <= upper_bound:
        # It's within range - detect direction
        if current_price > sma:
            return 'UP'  # Price rises towards SMA (bullish)
        else:
            return 'DOWN'  # Price falls towards SMA (bearish)

    return None
