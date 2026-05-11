import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, CLIENT_EMAIL
from database import get_alerts


def send_daily_report():
    """Sends daily alert report via Gmail (only TODAY's alerts)"""
    try:
        all_alerts = get_alerts(limit=10000)

        # Filter only TODAY's alerts
        today = datetime.now().strftime("%Y-%m-%d")
        today_alerts = [
            a for a in all_alerts if a['created_at'].startswith(today)]

        green_alerts = [a for a in today_alerts if a['direction'] == 'UP']
        red_alerts = [a for a in today_alerts if a['direction'] == 'DOWN']

        body = f"""
Daily Stock Alerts Report
Date: {datetime.now().strftime('%Y-%m-%d')}

GREEN ALERTS (Bullish - Price rising toward SMA):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if green_alerts:
            body += "Symbol | Price | SMA 200 | % from SMA\n"
            for alert in green_alerts[:20]:
                pct = ((alert['price'] - alert['sma_200']) /
                       alert['sma_200'] * 100)
                body += f"{alert['symbol']} | ${alert['price']:.2f} | ${alert['sma_200']:.2f} | {pct:+.2f}%\n"
        else:
            body += "No green alerts today\n"

        body += f"""
RED ALERTS (Bearish - Price falling toward SMA):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if red_alerts:
            body += "Symbol | Price | SMA 200 | % from SMA\n"
            for alert in red_alerts[:20]:
                pct = ((alert['price'] - alert['sma_200']) /
                       alert['sma_200'] * 100)
                body += f"{alert['symbol']} | ${alert['price']:.2f} | ${alert['sma_200']:.2f} | {pct:+.2f}%\n"
        else:
            body += "No red alerts today\n"

        body += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Alerts Today: {len(today_alerts)}
Green (Bullish): {len(green_alerts)}
Red (Bearish): {len(red_alerts)}

Login to dashboard: https://stock-alerts-ramon.onrender.com
Report generated automatically by Stock Alerts System
"""

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = "ramon@vanmeer.com, sameer.sahakari@gmail.com"
        msg['Subject'] = f"Stock Alerts Report - {datetime.now().strftime('%Y-%m-%d')}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email sent successfully")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_test_email():
    """Send a test email via Gmail"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = "ramon@vanmeer.com, sameer.sahakari@gmail.com"
        msg['Subject'] = "Stock Alerts System - Test Email"
        msg.attach(MIMEText(
            "This is a test email from Stock Alerts System. Gmail is working!", 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Test email sent successfully")
        return True

    except Exception as e:
        print(f"Error sending test email: {e}")
        return False
