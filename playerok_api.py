import requests

def get_playerok_items(item_name):
    url = "https://playerok.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    query = """
    query items($query: String!) {
      items(query: $query) {
        name
        price
        id
      }
    }
    """

    variables = {"query": item_name}

    data = {"query": query, "variables": variables}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Ошибка: {response.status_code} - {response.text}")
            return []

        result = response.json()
        items = result.get("data", {}).get("items", [])
        return [{"name": item["name"], "price": float(item["price"])} for item in items]
    except Exception as e:
        print(f"Ошибка при запросе к PlayerOK: {e}")
        return []
