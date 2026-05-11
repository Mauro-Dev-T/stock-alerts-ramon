from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from dotenv import load_dotenv

from config import DASHBOARD_USER, DASHBOARD_PASS, SECRET_KEY
from database import init_db, get_stocks, get_alerts, add_to_watchlist, remove_from_watchlist, get_stocks_with_watchlist
from stock_monitor import check_all_stocks
from email_service import send_daily_report

load_dotenv()

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

init_db()


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return User('1', DASHBOARD_USER)
    return None


def verify_password(username, password):
    return username == DASHBOARD_USER and password == DASHBOARD_PASS


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if verify_password(username, password):
            user = User('1', username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials'), 401
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    stocks = get_stocks_with_watchlist()
    alerts = get_alerts(limit=50)
    total_alerts = len(get_alerts(limit=10000))
    green_alerts = len([a for a in get_alerts(
        limit=10000) if a['direction'] == 'UP'])
    red_alerts = len([a for a in get_alerts(
        limit=10000) if a['direction'] == 'DOWN'])

    return render_template('dashboard.html',
                           stocks=stocks,
                           alerts=alerts,
                           total_alerts=total_alerts,
                           green_alerts=green_alerts,
                           red_alerts=red_alerts)


@app.route('/api/stocks')
@login_required
def api_stocks():
    stocks = get_stocks_with_watchlist()
    return jsonify(stocks)


@app.route('/api/alerts')
@login_required
def api_alerts():
    alerts = get_alerts(limit=50)
    return jsonify(alerts)


@app.route('/api/watchlist/add', methods=['POST'])
@login_required
def api_add_watchlist():
    data = request.json
    symbol = data.get('symbol', '').upper()
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
    add_to_watchlist(symbol)
    return jsonify({"status": "added", "symbol": symbol}), 200


@app.route('/api/watchlist/remove', methods=['POST'])
@login_required
def api_remove_watchlist():
    data = request.json
    symbol = data.get('symbol', '').upper()
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
    remove_from_watchlist(symbol)
    return jsonify({"status": "removed", "symbol": symbol}), 200


@app.route('/api/trigger-check')
@login_required
def api_trigger_check():
    """Manual trigger for stock check (testing)"""
    alerts = check_all_stocks()
    return jsonify({"status": "completed", "alerts_created": alerts}), 200


@app.route('/api/test-email')
@login_required
def api_test_email():
    from email_service import send_test_email
    result = send_test_email()
    return jsonify({"status": "sent" if result else "failed"}), 200


@app.route('/api/send-report')
@login_required
def api_send_report():
    from email_service import send_daily_report
    result = send_daily_report()
    return jsonify({"status": "sent" if result else "failed"}), 200


@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Daily check at 4:30 PM ET (market close)
    scheduler.add_job(check_all_stocks, 'cron', hour=21, minute=30)
    # Daily email at 5:00 PM ET
    scheduler.add_job(send_daily_report, 'cron', hour=22, minute=0)
    scheduler.start()
    print("Scheduler started - Daily check at 4:30 PM ET")


if __name__ == "__main__":
    start_scheduler()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
