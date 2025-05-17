import requests

class CSPriceChecker:
    def __init__(self):
        # Ключ — название скина (англ или рус), значение — market_hash_name (англ)
        self.name_to_market_hash = {}

    def load_skin_names(self):
        url = "https://market.csgo.com/api/v2/prices/class_instance/USD.json"
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get("items", {})
        
        for item in items.values():
            eng_name = item.get("market_hash_name")
            ru_name = item.get("ru_name")
            if eng_name:
                self.name_to_market_hash[eng_name.lower()] = eng_name
            if ru_name:
                self.name_to_market_hash[ru_name.lower()] = eng_name
        
           # print(eng_name, ru_name)

        print(f"Загружено названий: {len(self.name_to_market_hash)}")

    def get_price(self, market_hash_name: str) -> float | None:
        url = "https://market.csgo.com/api/v2/prices/USD.json"
        response = requests.get(url, timeout=10)
        data = response.json()
        items = data.get("items", [])
        for item in items:
            if item.get("market_hash_name") == market_hash_name:
                return float(item.get("price", 0))
        return None

    def find_price(self, skin_name: str) -> float | None:
        key = skin_name.lower()
        print(skin_name)
        market_hash_name = self.name_to_market_hash.get(key)
        print(f"Результат {market_hash_name}")
        if not market_hash_name:
            return None
        return self.get_price(market_hash_name)


if __name__ == "__main__":
    checker = CSPriceChecker()
    print("Загружаем названия скинов...")
    checker.load_skin_names()

    while True:
        skin = input("Введите название скина (англ или рус): ").strip()
        if not skin:
            break
        price = checker.find_price(skin)
        if price is not None:
            print(f"Цена скина '{skin}': {price} USD")
        else:
            print(f"Скин '{skin}' не найден или цена отсутствует.")
