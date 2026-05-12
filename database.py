import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Stock table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            price REAL,
            sma_200 REAL,
            last_check TEXT,
            monitored BOOLEAN DEFAULT 1
        )
    """)

    # Table alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER,
            symbol TEXT NOT NULL,
            direction TEXT,
            price REAL,
            sma_200 REAL,
            threshold REAL,
            created_at TEXT NOT NULL,
            sent_to_email BOOLEAN DEFAULT 0,
            FOREIGN KEY (stock_id) REFERENCES stocks(id)
        )
    """)

    conn.commit()

    # Poblar tabla stocks con todos los símbolos
    from stock_monitor import ALL_STOCKS
    for symbol in ALL_STOCKS:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO stocks (symbol, monitored) VALUES (?, 1)", (symbol,))
        except:
            pass

    conn.commit()
    conn.close()


def get_stocks(limit=None):
    conn = get_connection()
    cursor = conn.cursor()

    if limit:
        cursor.execute(
            "SELECT * FROM stocks WHERE monitored=1 ORDER BY symbol LIMIT ?", (limit,))
    else:
        cursor.execute(
            "SELECT * FROM stocks WHERE monitored=1 ORDER BY symbol")

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_alerts(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_alert(symbol, direction, price, sma_200, threshold):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (symbol, direction, price, sma_200, threshold, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (symbol, direction, price, sma_200, threshold, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def add_stock(symbol):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO stocks (symbol, monitored) VALUES (?, 1)", (symbol,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def add_to_watchlist(symbol):
    """Add stock to watchlist"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE stocks SET monitored=1 WHERE symbol=?", (symbol,))
    conn.commit()
    conn.close()


def remove_from_watchlist(symbol):
    """Remove stock from watchlist"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE stocks SET monitored=0 WHERE symbol=?", (symbol,))
    conn.commit()
    conn.close()


def get_stocks_with_watchlist():
    """Get all stocks with watchlist status"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT symbol, monitored as in_watchlist FROM stocks ORDER BY symbol")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
