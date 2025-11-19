import requests
from bs4 import BeautifulSoup

def get_funpay_items(category="csgo", limit=50):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        # "Cookie": "sessionid=your_sessionid; csrftoken=your_csrftoken"  # Можно убрать, если не нужна авторизация
    }

    # Если категория "roblox" — делаем поиск по слову "Roblox"
    if category == "roblox":
        url = "https://funpay.ru/search?query=Roblox"
    else:
        url = f"https://funpay.ru/lots/{category}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при запросе к FunPay: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    items = []
    for item in soup.select(".lot-card"):
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
