# Stock Alerts System - Ramon Van Meer

Professional stock monitoring system with real-time alerts and automated email reports.

## Features

- **365 Stocks Monitored Daily** - Top 200 from S&P 500, Nasdaq, and Dow Jones
- **SMA 200 Calculation** - Real-time 200-day moving average
- **Alert Detection** - Automatic alerts when price is within 1% of SMA
- **Color-Coded Alerts**:
  - GREEN = Price rising toward SMA (Bullish)
  - RED = Price falling toward SMA (Bearish)
- **Real-Time Dashboard** - 24/7 access to all alerts and history
- **Automated Email Reports** - Daily at 4:30 PM ET (after market close)
- **Watchlist Management** - Add/remove stocks from monitoring

## Tech Stack

- **Backend**: Python 3 + Flask
- **API**: Polygon.io (real-time stock data)
- **Database**: SQLite
- **Deployment**: Render (24/7 monitoring)
- **Email**: Gmail SMTP automation

## Live System

**URL**: https://stock-alerts-ramon.onrender.com

## How It Works

1. **4:15 PM ET Daily**: System checks all 365 stocks
2. **SMA Calculation**: 200-day moving average computed for each stock
3. **Alert Detection**: Alerts triggered when price within 1% of SMA
4. **4:30 PM ET**: Automated email sent with all alerts from that day
5. **Dashboard**: Real-time updates showing alert history

## Repository

GitHub: https://github.com/Mauro-Dev-T/stock-alerts-ramon

## Author

**Mauricio Leiva** - Python Developer | Trading Automation Specialist

**System Status**: ✅ Live and monitoring 24/7
