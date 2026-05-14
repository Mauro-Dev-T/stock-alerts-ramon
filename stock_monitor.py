import time
from datetime import datetime
from config import ALERT_THRESHOLD
from database import get_stocks, add_stock, save_alert
from polygon_service import get_historical_data, calculate_sma, check_alert_condition, get_stock_price

# ── TOP 200 S&P 500 ──
SP500_STOCKS = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK.B', 'UNH',
    'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'LLY',
    'ABBV', 'PEP', 'COST', 'AVGO', 'KO', 'WMT', 'BAC', 'MCD', 'CSCO', 'TMO',
    'ACN', 'ABT', 'CRM', 'WFC', 'NEE', 'TXN', 'DHR', 'PM', 'LIN', 'MS',
    'INTC', 'UNP', 'AMD', 'RTX', 'BMY', 'AMGN', 'ADBE', 'QCOM', 'LOW', 'INTU',
    'SPGI', 'HON', 'CAT', 'DE', 'GS', 'BLK', 'AXP', 'SBUX', 'T', 'GE',
    'ELV', 'AMAT', 'GILD', 'MDT', 'ISRG', 'ADI', 'BKNG', 'REGN', 'VRTX', 'CVS',
    'TJX', 'MO', 'C', 'PLD', 'LRCX', 'ADP', 'MMC', 'ZTS', 'KLAC', 'CI',
    'EOG', 'SLB', 'ITW', 'CME', 'FDX', 'APD', 'MCO', 'D', 'DUK', 'SO',
    'USB', 'NSC', 'BSX', 'NOC', 'PNC', 'ICE', 'AON', 'CL', 'SNPS', 'CDNS',
    'EMR', 'ETN', 'FCX', 'HCA', 'ORLY', 'MPC', 'PSA', 'CTAS', 'TGT', 'SHW',
    'VLO', 'PSX', 'GD', 'BDX', 'MAR', 'MRNA', 'MNST', 'AIG', 'F', 'GM',
    'ECL', 'EW', 'DXCM', 'CTSH', 'OXY', 'WELL', 'A', 'HUM', 'FTNT', 'CARR',
    'STZ', 'ROST', 'MSI', 'IDXX', 'ROP', 'PCAR', 'AZO', 'WMB', 'KMB', 'TEL',
    'FAST', 'ODFL', 'EXC', 'PPG', 'VRSK', 'OTIS', 'HSY', 'YUM', 'SYK', 'ZBH',
    'KEYS', 'CPRT', 'LHX', 'NUE', 'AME', 'TDG', 'CSGP', 'DLTR', 'KR', 'BAX',
    'CTVA', 'BIIB', 'HES', 'DVN', 'ALB', 'XYL', 'IQV', 'ALGN', 'VRSN', 'AWK',
    'LUV', 'DAL', 'UAL', 'AAL', 'CCL', 'RCL', 'NCLH', 'MGM', 'WYNN', 'LVS',
    'DG', 'ULTA', 'BBY', 'KSS', 'M', 'JWN', 'GPS', 'LEVI', 'PVH', 'RL',
    'NKE', 'UAA', 'HBI', 'COH', 'TIF', 'SIG', 'GPC', 'AAN', 'KMX', 'AN',
]

# ── TOP 200 NASDAQ ──
NASDAQ_STOCKS = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'AVGO', 'ASML',
    'CSCO', 'ADBE', 'AMD', 'INTC', 'QCOM', 'INTU', 'AMAT', 'LRCX', 'KLAC', 'SNPS',
    'CDNS', 'ADI', 'MRVL', 'NXPI', 'MCHP', 'ON', 'TER', 'MPWR', 'SWKS', 'QRVO',
    'ORCL', 'CRM', 'WDAY', 'NOW', 'TEAM', 'DDOG', 'ZS', 'CRWD', 'OKTA', 'NET',
    'PANW', 'FTNT', 'CYBR', 'S', 'VRNS', 'QLYS', 'TENB', 'RPM', 'JNPR', 'F5',
    'AMGN', 'GILD', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'ILMN', 'IDXX', 'ALGN', 'DXCM',
    'ISRG', 'HOLX', 'ABMD', 'XRAY', 'HSIC', 'PDCO', 'MMSI', 'NVCR', 'SILK', 'NVAX',
    'COST', 'SBUX', 'MDLZ', 'MNST', 'KHC', 'WBA', 'DLTR', 'FAST', 'ODFL', 'PCAR',
    'CPRT', 'VRSK', 'CTAS', 'PAYX', 'ADP', 'CINF', 'ERIE', 'FITB', 'HBAN', 'NTRS',
    'TSCO', 'POOL', 'ULTA', 'ROST', 'ORLY', 'AZO', 'BKNG', 'EXPE', 'TRIP', 'ABNB',
    'NFLX', 'ROKU', 'SPOT', 'ZM', 'DOCU', 'PTON', 'LYFT', 'UBER', 'DASH',
    'PYPL', 'SQ', 'AFRM', 'UPST', 'LC', 'SOFI', 'HOOD', 'COIN',
    'MELI', 'SE', 'GRAB', 'JD', 'PDD', 'BIDU', 'NTES', 'VIPS',
    'ZI', 'GTLB', 'CFLT', 'MDB', 'ESTC', 'DT', 'HUBS',
    'BILL', 'PCTY', 'PAYC', 'JAMF', 'APPN', 'FIVN', 'NICE',
    'NTAP', 'STX', 'WDC', 'SMCI', 'PSTG', 'NTNX', 'ANET', 'JNPR', 'DELL',
    'LSCC', 'TTWO', 'EA', 'RBLX', 'U', 'DKNG',
    'PENN', 'HIMS', 'TDOC', 'NVAX',
    'XPEV', 'NIO', 'LI', 'RIVN', 'LCID',
]

# ── TOP 200 DOW JONES ──
DOW_STOCKS = [
    'AAPL', 'MSFT', 'JPM', 'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'DIS',
    'NKE', 'MCD', 'IBM', 'GS', 'CAT', 'AXP', 'MMM', 'BA', 'CVX', 'KO',
    'MRK', 'DOW', 'HON', 'CRM', 'WBA', 'VZ', 'AMGN', 'TRV', 'RTX',
    'XOM', 'BAC', 'C', 'WFC', 'USB', 'PNC', 'TFC', 'COF', 'MET',
    'PRU', 'AFL', 'ALL', 'CB', 'MMC', 'AON', 'HIG', 'IVZ', 'STT',
    'BK', 'SCHW', 'MS', 'BLK',
    'ABT', 'MDT', 'SYK', 'BSX', 'EW', 'ZBH', 'BAX', 'BDX', 'CAH', 'MCK',
    'HSIC', 'PDCO', 'XRAY', 'DXCM', 'ISRG', 'HOLX', 'ALGN', 'STE',
    'GE', 'ETN', 'EMR', 'ITW', 'ROK', 'AME', 'PH', 'DOV', 'XYL',
    'CARR', 'OTIS', 'TDG', 'LHX', 'NOC', 'GD', 'LMT', 'HII',
    'DE', 'AGCO', 'PCAR', 'CMI',
    'UNP', 'CSX', 'NSC', 'WAB',
    'UPS', 'FDX', 'EXPD', 'CHRW', 'JBHT', 'ODFL', 'SAIA',
    'DAL', 'UAL', 'LUV', 'AAL', 'ALK',
    'CVS', 'CI', 'HUM', 'CNC', 'ELV',
    'DUK', 'SO', 'NEE', 'EXC', 'D', 'AEP', 'SRE',
    'T', 'VZ', 'TMUS', 'SIRI', 'CHTR', 'CMCSA',
    'NFLX', 'PARA',
    'OMC',
    'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'SPG', 'O', 'WELL', 'PSA', 'EQR',
]

# Combine all stocks (unique)
ALL_STOCKS = list(set(SP500_STOCKS + NASDAQ_STOCKS + DOW_STOCKS))
print(f"Total unique stocks to monitor: {len(ALL_STOCKS)}")


def check_all_stocks():
    """
    Check all stocks and create alerts if price is within 1% of SMA 200.
    Runs daily from the scheduler. Sends email report automatically at the end.
    """
    print(
        f"[{datetime.now()}] Starting daily stock check for {len(ALL_STOCKS)} stocks...")

    alerts_created = 0
    errors = 0
    skipped = 0

    for i, symbol in enumerate(ALL_STOCKS):
        try:
            # Add stock to database if not exists
            add_stock(symbol)

            # Get historical data (200+ days)
            prices = get_historical_data(symbol, days=200)

            # Rate limit: sleep between requests
            time.sleep(0.3)

            if not prices or len(prices) < 200:
                skipped += 1
                continue

            # Calculate SMA 200
            sma_200 = calculate_sma(prices, period=200)

            if sma_200 is None:
                skipped += 1
                continue

            # Get current price (last price in historical data)
            current_price = prices[-1]

            # Check alert condition (1% threshold)
            direction = check_alert_condition(
                symbol, current_price, sma_200, ALERT_THRESHOLD
            )

            if direction:
                save_alert(symbol, direction, current_price,
                           sma_200, ALERT_THRESHOLD)
                print(
                    f"  ✓ Alert: {symbol} {direction} | Price: ${current_price:.2f} | SMA200: ${sma_200:.2f}")
                alerts_created += 1

            # Progress update every 50 stocks
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(ALL_STOCKS)} stocks checked...")

        except Exception as e:
            print(f"  ✗ Error processing {symbol}: {e}")
            errors += 1
            continue

    print(f"[{datetime.now()}] Check completed: {alerts_created} alerts | {skipped} skipped | {errors} errors")

    # Send daily email report automatically after check
    try:
        from email_service import send_daily_report
        send_daily_report()
        print(f"[{datetime.now()}] Daily email report sent successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Error sending daily email: {e}")

    return alerts_created


def check_all_stocks_now():
    """Manual trigger for testing"""
    return check_all_stocks()
