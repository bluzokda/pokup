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
