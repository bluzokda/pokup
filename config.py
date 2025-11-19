from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ARBITRAGE_THRESHOLD = int(os.getenv("ARBITRAGE_THRESHOLD", 50))  # по умолчанию 50 руб.
