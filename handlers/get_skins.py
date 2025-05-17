from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
from datetime import datetime

router = Router()

class FilterByDate(StatesGroup):
    waiting_for_date = State()

@router.message(lambda message: message.text == "📅 Показать скины по дате")
async def ask_date(message: types.Message, state: FSMContext):
    await state.clear()  # ← ОЧИСТКА ПРЕДЫДУЩИХ СОСТОЯНИЙ
    current_state = await state.get_state()
    await message.answer(f"Состояние после очистки: {current_state}")
    await message.answer("Введите дату в формате ГГГГ-ММ-ДД:")
    await state.set_state(FilterByDate.waiting_for_date)

@router.message(FilterByDate.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    try:
        # Проверяем формат даты
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Попробуйте снова в формате ГГГГ-ММ-ДД.")
        return

    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, purchase_price, market_price, final_price, profit_percent, purchase_date "
        "FROM skins WHERE purchase_date = ? ORDER BY purchase_date DESC",
        (date_text,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await message.answer(f"Скинов за дату {date_text} не найдено.")
    else:
        response_lines = [f"Скины за {date_text}:\n"]
        for i, row in enumerate(rows, start=1):
            name, purchase_price, market_price, final_price, profit_percent, purchase_date = row
            response_lines.append(
                f"{i}. {name}\n"
                f"   Дата покупки: {purchase_date}\n"
                f"   Цена покупки: ${purchase_price:.2f}\n"
                f"   Цена на маркете: ${market_price:.2f}\n"
                f"   Цена после комиссий: ${final_price:.2f}\n"
                f"   {'📈 Выгода' if profit_percent > 0 else '📉 Убыток'}: {profit_percent:.2f}%\n"
            )
        await message.answer("\n".join(response_lines))

    await state.clear()
