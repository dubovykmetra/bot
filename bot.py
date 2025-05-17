import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import requests

BOT_TOKEN = "7869776078:AAFTZtTFOrZ1qrqM8Vkz9S1jiYyKGmBn1zI"  # Замени на свой токен

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AddSkin(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()

def get_usd_exchange_rate():
    try:
        response = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5", timeout=10)
        data = response.json()
        usd = next(item for item in data if item["ccy"] == "USD")
        return float(usd["sale"])
    except:
        return 41.75

def get_skin_price_from_api(skin_name):
    url = "https://market.csgo.com/api/v2/prices/USD.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        found = next((item for item in items if item["market_hash_name"] == skin_name), None)
        return float(found["price"]) if found else None
    except:
        return None

def init_db():
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        purchase_price REAL,
        market_price REAL,
        final_price REAL,
        profit_percent REAL,
        purchase_date TEXT
    )
    ''')
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь команду /add чтобы добавить новый скин.")

@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    await message.answer("Введите название скина:")
    await state.set_state(AddSkin.waiting_for_name)

@dp.message(AddSkin.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену покупки (в $ или грн, например $2.5 или 1000):")
    await state.set_state(AddSkin.waiting_for_price)

@dp.message(AddSkin.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data["name"]
    text = message.text.replace(",", ".")
    rate = get_usd_exchange_rate()

    try:
        if text.startswith("$"):
            purchase_price = float(text[1:])
        else:
            uah = float(text)
            purchase_price = uah / rate
    except:
        await message.answer("❌ Неверный формат цены. Повторите ввод.")
        return

    market_price = get_skin_price_from_api(name)
    if market_price is None:
        await message.answer(f"❌ Скин с именем «{name}» не найден. Попробуйте снова.\nВведите название скина:")
        await state.clear()
        await state.set_state(AddSkin.waiting_for_name)
        return  # ВАЖНО: прерываем дальнейшее выполнение
    else:
        final_price = market_price * 0.95 * 0.95
        profit = (final_price - purchase_price * 1.042) / purchase_price * 100

    purchase_price *= 1.042
    purchase_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO skins (name, purchase_price, market_price, final_price, profit_percent, purchase_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, purchase_price, market_price, final_price, profit, purchase_date))
    conn.commit()
    conn.close()

    await message.answer(
        f"✅ Скин: {name}\n"
        f"Дата покупки: {purchase_date}\n"
        f"Цена покупки: ${purchase_price:.2f}\n"
        f"Цена на маркете: ${market_price:.2f}\n"
        f"Цена после комиссий: ${final_price:.2f}\n"
        f"{'📈 Выгода' if profit > 0 else '📉 Убыток'}: {profit:.2f}%"
    )

    await state.clear()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
