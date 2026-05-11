import requests
from datetime import datetime, timedelta
from config import POLYGON_API_KEY

BASE_URL = "https://api.polygon.io/v2"


def get_stock_price(symbol):
    """Gets the most recent closing price of a stock"""
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        url = f"{BASE_URL}/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {"sort": "desc", "limit": 1, "apiKey": POLYGON_API_KEY}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                return float(results[0]['c'])
        return None
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None


def get_historical_data(symbol, days=200):
    """Gets historical closing prices for last N days"""
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days+120)
                      ).strftime("%Y-%m-%d")

        url = f"{BASE_URL}/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {"sort": "asc", "limit": 300, "apiKey": POLYGON_API_KEY}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            prices = [float(r['c']) for r in results[-days:]]
            return prices
        return []
    except Exception as e:
        print(f"Error getting historical data for {symbol}: {e}")
        return []


def calculate_sma(prices, period=200):
    """Calculate simple moving average"""
    if not prices or len(prices) < period:
        return None
    sma = sum(prices[-period:]) / period
    return round(sma, 2)


def check_alert_condition(symbol, current_price, sma, threshold=0.01):
    """
    Detects if price is within 1% of SMA 200
    Returns: None, 'UP' (bullish), or 'DOWN' (bearish)
    """
    if current_price is None or sma is None:
        return None

    upper_bound = sma * (1 + threshold)
    lower_bound = sma * (1 - threshold)

    if lower_bound <= current_price <= upper_bound:
        if current_price >= sma:
            return 'UP'
        else:
            return 'DOWN'
    return None
