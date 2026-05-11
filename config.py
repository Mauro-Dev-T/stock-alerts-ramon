import os
from dotenv import load_dotenv

load_dotenv()

# Dashboard credentials
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "vanmeer")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS", "vanmeersalerts2026$")

# Polygon.io API
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_SMTP = os.getenv("EMAIL_SMTP", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "alerts.db")

# Secret key for Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Client email (where to send alerts)
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "")

# Alert threshold (1%)
ALERT_THRESHOLD = 0.01

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
