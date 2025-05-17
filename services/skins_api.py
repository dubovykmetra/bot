import requests

def get_skin_price_from_api(skin_name: str) -> float | None:
    url = "https://market.csgo.com/api/v2/prices/USD.json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get("items", [])
        found = next((item for item in items if item["market_hash_name"] == skin_name), None)
        return float(found["price"]) if found else None
    except:
        return None
