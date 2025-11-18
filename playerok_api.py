import requests
from config import PLAYEROK_API_KEY

def get_playerok_items(item_name):
    headers = {"Authorization": f"Bearer {PLAYEROK_API_KEY}"}
    url = f"https://playerok.com/api/v1/items"
    params = {"name": item_name}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    items = []
    for item in data.get("items", []):
        name = item.get("name")
        price = item.get("price")
        if name and price:
            items.append({"name": name, "price": float(price)})
    return items
