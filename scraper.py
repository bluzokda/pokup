import requests
from bs4 import BeautifulSoup

def get_funpay_items(category="csgo", limit=50):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        # "Cookie": "sessionid=your_sessionid; csrftoken=your_csrftoken"  # Можно убрать, если не нужна авторизация
    }

    # Словарь с правильными URL для категорий
    category_urls = {
        "csgo": "https://funpay.com/lots/csgo",
        "dota2": "https://funpay.com/lots/dota2",
        "rust": "https://funpay.com/lots/rust",
        "cs2": "https://funpay.com/lots/cs2",
        "roblox": "https://funpay.com/chips/99/"  # Правильная ссылка для Roblox (с .com)
    }

    url = category_urls.get(category)

    if not url:
        print(f"Неизвестная категория: {category}")
        return []

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при запросе к FunPay: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    items = []
    for item in soup.select(".lot-card"):  # Убедись, что селектор правильный
        name = item.select_one(".title a")
        price = item.select_one(".price")
        if not name or not price:
            continue
        name = name.text.strip()
        try:
            price = float(price.text.replace(" ", "").replace("₽", ""))
        except:
            continue
        items.append({"name": name, "price": price})
    return items[:limit]
