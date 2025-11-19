from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ARBITRAGE_THRESHOLD = int(os.getenv("ARBITRAGE_THRESHOLD", 50))  

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(profit) FROM deals")
    row = c.fetchone()
    conn.close()
    total_deals = row[0] or 0
    total_profit = row[1] or 0.0
    return total_deals, total_profit
