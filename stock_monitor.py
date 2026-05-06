from datetime import datetime
from config import ALERT_THRESHOLD
from database import get_stocks, add_stock, save_alert
from polygon_service import get_historical_data, calculate_sma, check_alert_condition

# Top 200 stocks for each index (simplified, the most popular)
SP500_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN',
                'NVDA', 'TSLA', 'META', 'BRK.B', 'JNJ', 'V']
NASDAQ_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN',
                 'NVDA', 'TESLA', 'META', 'ASML', 'AVGO', 'CSCO']
DOW_STOCKS = ['AAPL', 'MSFT', 'JPM', 'JNJ',
              'V', 'WMT', 'PG', 'UNH', 'HD', 'DIS']

ALL_STOCKS = list(set(SP500_STOCKS + NASDAQ_STOCKS + DOW_STOCKS))


def check_all_stocks():
    """
    Check all stock levels and create alerts if needed.
    This function runs daily from the scheduler.
    """
    print(f"[{datetime.now()}] Starting stock check for {len(ALL_STOCKS)} stocks...")

    alerts_created = 0

    for symbol in ALL_STOCKS:
        try:
            # Add stock to database if not exists
            add_stock(symbol)

            # Get historical data
            prices = get_historical_data(symbol)

            if not prices:
                print(f"No data for {symbol}")
                continue

            # Calculate SMA 200
            sma_200 = calculate_sma(prices, period=200)

            if sma_200 is None:
                continue

            # Get current price (last price in data)
            current_price = prices[-1]

            # Check alert condition
            direction = check_alert_condition(
                symbol, current_price, sma_200, ALERT_THRESHOLD)

            if direction:
                # Save alert to database
                save_alert(symbol, direction, current_price,
                           sma_200, ALERT_THRESHOLD)
                print(
                    f"✓ Alert created: {symbol} {direction} (Price: ${current_price:.2f}, SMA: ${sma_200:.2f})")
                alerts_created += 1

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    print(f"[{datetime.now()}] Stock check completed. {alerts_created} alerts created.")
    return alerts_created


def check_all_stocks_now():
    """Auxiliary function for manual testing"""
    return check_all_stocks()
