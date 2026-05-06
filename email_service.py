import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP, EMAIL_PORT, CLIENT_EMAIL
from database import get_alerts


def send_daily_report():
    """Sends daily alert reports via email"""
    try:
        alerts = get_alerts(limit=10000)

        if not alerts:
            return False

        green_alerts = [a for a in alerts if a['direction'] == 'UP']
        red_alerts = [a for a in alerts if a['direction'] == 'DOWN']

        # Build email body
        body = f"""
Daily Stock Alerts Report
Date: {datetime.now().strftime('%Y-%m-%d')}

GREEN ALERTS (Bullish - Price rising toward SMA):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if green_alerts:
            body += "Symbol | Price | SMA 200 | % from SMA\n"
            for alert in green_alerts[:10]:
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
            for alert in red_alerts[:10]:
                pct = ((alert['price'] - alert['sma_200']) /
                       alert['sma_200'] * 100)
                body += f"{alert['symbol']} | ${alert['price']:.2f} | ${alert['sma_200']:.2f} | {pct:+.2f}%\n"
        else:
            body += "No red alerts today\n"

        body += f"""

Total Alerts Today: {len(alerts)}
Green (Bullish): {len(green_alerts)}
Red (Bearish): {len(red_alerts)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Report generated automatically by Stock Alerts System
Login to dashboard: http://localhost:5000
"""

        # Send email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = CLIENT_EMAIL
        msg['Subject'] = f"Stock Alerts Report - {datetime.now().strftime('%Y-%m-%d')}"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email sent to {CLIENT_EMAIL}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_test_email():
    """Send a test email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = CLIENT_EMAIL
        msg['Subject'] = "Stock Alerts System - Test Email"

        body = "This is a test email from Stock Alerts System. Email configuration is working!"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Test email sent to {CLIENT_EMAIL}")
        return True

    except Exception as e:
        print(f"Error sending test email: {e}")
        return False
