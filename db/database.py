import sqlite3

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

def add_skin_to_db(name, purchase_price, market_price, final_price, profit_percent, purchase_date):
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO skins (name, purchase_price, market_price, final_price, profit_percent, purchase_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, purchase_price, market_price, final_price, profit_percent, purchase_date))
    conn.commit()
    conn.close()
