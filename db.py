import sqlite3

DB_NAME = "arbitrage.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            fp_price REAL,
            po_price REAL,
            profit REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Новая таблица для категорий
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_categories (
            user_id INTEGER PRIMARY KEY,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_deal(item_name, fp_price, po_price, profit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO deals (item_name, fp_price, po_price, profit)
        VALUES (?, ?, ?, ?)
    """, (item_name, fp_price, po_price, profit))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(profit) FROM deals")
    row = c.fetchone()
    conn.close()
    total_deals = row[0] or 0
    total_profit = row[1] or 0.0
    return total_deals, total_profit

def set_user_category(user_id, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO user_categories (user_id, category)
        VALUES (?, ?)
    """, (user_id, category))
    conn.commit()
    conn.close()

def get_user_category(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category FROM user_categories WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
