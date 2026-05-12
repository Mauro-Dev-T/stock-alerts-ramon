import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        import sqlite3
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
    return conn


def _is_postgres():
    return bool(os.getenv("DATABASE_URL"))


def init_db():
    """Create the tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    if _is_postgres():
        # PostgreSQL syntax
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id SERIAL PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                price REAL,
                sma_200 REAL,
                last_check TEXT,
                monitored BOOLEAN DEFAULT TRUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                stock_id INTEGER,
                symbol TEXT NOT NULL,
                direction TEXT,
                price REAL,
                sma_200 REAL,
                threshold REAL,
                created_at TEXT NOT NULL,
                sent_to_email BOOLEAN DEFAULT FALSE
            )
        """)
    else:
        # SQLite syntax
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
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
            if _is_postgres():
                cursor.execute(
                    "INSERT INTO stocks (symbol, monitored) VALUES (%s, TRUE) ON CONFLICT (symbol) DO NOTHING", (symbol,))
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO stocks (symbol, monitored) VALUES (?, 1)", (symbol,))
        except:
            pass

    conn.commit()
    conn.close()


def get_stocks(limit=None):
    conn = get_connection()
    cursor = conn.cursor()

    if _is_postgres():
        if limit:
            cursor.execute(
                "SELECT * FROM stocks WHERE monitored=TRUE ORDER BY symbol LIMIT %s", (limit,))
        else:
            cursor.execute(
                "SELECT * FROM stocks WHERE monitored=TRUE ORDER BY symbol")
    else:
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
    if _is_postgres():
        cursor.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT %s", (limit,))
    else:
        cursor.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_alert(symbol, direction, price, sma_200, threshold):
    conn = get_connection()
    cursor = conn.cursor()
    if _is_postgres():
        cursor.execute("""
            INSERT INTO alerts (symbol, direction, price, sma_200, threshold, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (symbol, direction, price, sma_200, threshold, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
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
        if _is_postgres():
            cursor.execute(
                "INSERT INTO stocks (symbol, monitored) VALUES (%s, TRUE) ON CONFLICT (symbol) DO NOTHING", (symbol,))
        else:
            cursor.execute(
                "INSERT OR IGNORE INTO stocks (symbol, monitored) VALUES (?, 1)", (symbol,))
        conn.commit()
    except Exception:
        pass
    conn.close()


def add_to_watchlist(symbol):
    conn = get_connection()
    cursor = conn.cursor()
    if _is_postgres():
        cursor.execute(
            "UPDATE stocks SET monitored=TRUE WHERE symbol=%s", (symbol,))
    else:
        cursor.execute(
            "UPDATE stocks SET monitored=1 WHERE symbol=?", (symbol,))
    conn.commit()
    conn.close()


def remove_from_watchlist(symbol):
    conn = get_connection()
    cursor = conn.cursor()
    if _is_postgres():
        cursor.execute(
            "UPDATE stocks SET monitored=FALSE WHERE symbol=%s", (symbol,))
    else:
        cursor.execute(
            "UPDATE stocks SET monitored=0 WHERE symbol=?", (symbol,))
    conn.commit()
    conn.close()


def get_stocks_with_watchlist():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT symbol, monitored as in_watchlist FROM stocks ORDER BY symbol")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
