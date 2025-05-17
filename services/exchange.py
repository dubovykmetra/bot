import requests

def get_usd_exchange_rate():
    try:
        response = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5", timeout=10)
        data = response.json()
        usd = next(item for item in data if item["ccy"] == "USD")
        return float(usd["sale"])
    except:
        return 41.75
