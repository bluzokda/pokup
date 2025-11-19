import requests
from bs4 import BeautifulSoup
import asyncio

def get_funpay_items(category="csgo", limit=50):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    category_urls = {
        "csgo": "https://funpay.com/lots/csgo",
        "dota2": "https://funpay.com/lots/dota2",
        "rust": "https://funpay.com/lots/rust",
        "cs2": "https://funpay.com/lots/cs2",
        "roblox": "https://funpay.com/chips/99/"
    }

    url = category_urls.get(category)

    if not url:
        print(f"Неизвестная категория: {category}")
        return []

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка при запросе к FunPay: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        items = []
        for item in soup.select(".lot-card"):
            name_elem = item.select_one(".title a")
            price_elem = item.select_one(".price")
            if not name_elem or not price_elem:
                continue
            name = name_elem.text.strip()
            try:
                price = float(price_elem.text.replace(" ", "").replace("₽", ""))
            except:
                continue
            # FunPay не возвращает ID напрямую в карточке, но можно попробовать извлечь из href
            href = name_elem.get("href", "")
            item_id = href.split("/")[-2] if "/lots/" in href else None
            items.append({"id": item_id, "name": name, "price": price})
        return items[:limit]
    except Exception as e:
        print(f"Ошибка при парсинге FunPay: {e}")
        return []
