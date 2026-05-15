import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, EMAIL_ADDRESS
from database import get_alerts


FROM_EMAIL = EMAIL_ADDRESS
TO_EMAILS = ["ramon@vanmeer.com", "sameer.sahakari@gmail.com"]


def _send_via_sendgrid(subject: str, body: str) -> bool:
    """Envía un email vía SendGrid API. Retorna True si fue exitoso."""
    try:
        if not SENDGRID_API_KEY:
            print("Error: SENDGRID_API_KEY is not configured", flush=True)
            return False

        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAILS,
            subject=subject,
            plain_text_content=body,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if 200 <= response.status_code < 300:
            print(
                f"Email sent successfully via SendGrid (status {response.status_code})", flush=True)
            return True
        else:
            print(
                f"SendGrid returned non-success status: {response.status_code}", flush=True)
            print(f"Response body: {response.body}", flush=True)
            return False

    except Exception as e:
        print(
            f"Error sending email via SendGrid: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def send_daily_report():
    """Sends daily alert report via SendGrid (only TODAY's alerts)"""
    try:
        all_alerts = get_alerts(limit=10000)

        # Filter only TODAY's alerts
        today = datetime.now().strftime("%Y-%m-%d")
        today_alerts = [
            a for a in all_alerts if a['created_at'].startswith(today)]

        green_alerts = [a for a in today_alerts if a['direction'] == 'UP']
        red_alerts = [a for a in today_alerts if a['direction'] == 'DOWN']

        body = f"""Daily Stock Alerts Report
Date: {datetime.now().strftime('%Y-%m-%d')}

GREEN ALERTS (Bullish - Price rising toward SMA):
----------------------------------------------------------
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
----------------------------------------------------------
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
----------------------------------------------------------
Total Alerts Today: {len(today_alerts)}
Green (Bullish): {len(green_alerts)}
Red (Bearish): {len(red_alerts)}

Login to dashboard: https://stock-alerts-ramon.onrender.com
Report generated automatically by Stock Alerts System
"""

        subject = f"Stock Alerts Report - {datetime.now().strftime('%Y-%m-%d')}"
        result = _send_via_sendgrid(subject, body)

        if result:
            print(
                f"[{datetime.now()}] Daily email report sent successfully", flush=True)

        return result

    except Exception as e:
        print(
            f"Error building daily report: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def send_test_email():
    """Sends a test email via SendGrid"""
    subject = "Stock Alerts System - Test Email"
    body = "This is a test email from Stock Alerts System. SendGrid is working!"
    return _send_via_sendgrid(subject, body)
