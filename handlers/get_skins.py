from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
from datetime import datetime
from states.get_skins import FilterByDate
from keyboards.reply import skin_list
from keyboards.reply import main_menu

router = Router()


@router.message(lambda message: message.text == "Показать скины по дате")
async def ask_date(message: types.Message, state: FSMContext):
    await state.clear()  # ← ОЧИСТКА ПРЕДЫДУЩИХ СОСТОЯНИЙ
    # current_state = await state.get_state()
    # await message.answer(f"Состояние после очистки: {current_state}")
   # await message.answer("Введите дату в формате ГГГГ-ММ-ДД:")
    await message.answer(
        "Вы хотите использовать сегодняшнюю дату или ввести свою?",
        reply_markup=skin_list
    )
    await state.set_state(FilterByDate.waiting_for_datess)

    

@router.message(FilterByDate.waiting_for_datess)
async def process_date(message: types.Message, state: FSMContext):
    text = message.text.strip()
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    if text == "📅 Сегодня":
        date_text = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT name, purchase_price, market_price, final_price, profit_percent, purchase_date "
            "FROM skins WHERE purchase_date = ? ORDER BY purchase_date DESC",
            (date_text,)
        )
        rows = cursor.fetchall()

    elif text == "✍️ Ввести вручную":
        await message.answer("Введите дату в формате ГГГГ-ММ-ДД:")
        await state.set_state(FilterByDate.waiting_for_manual_date)
        conn.close()
        return

    elif text == "За все дни":
        date_text = "все даты"
        cursor.execute(
            "SELECT name, purchase_price, market_price, final_price, profit_percent, purchase_date "
            "FROM skins ORDER BY purchase_date DESC"
        )
        rows = cursor.fetchall()
    else:
        await message.answer("Неверная команда.")
        conn.close()
        return

    conn.close()

    if not rows:
        await message.answer(f"Скинов за дату {date_text} не найдено.")
        return

    # Отправка чанками по 5
    CHUNK_SIZE = 5
    for i in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[i:i + CHUNK_SIZE]
        response_lines = [f"Скины за {date_text}:\n"]
        for idx, row in enumerate(chunk, start=i + 1):
            name, purchase_price, market_price, final_price, profit_percent, purchase_date = row
            response_lines.append(
                f"{idx}. {name}\n"
                f"   Дата покупки: {purchase_date}\n"
                f"   Цена покупки: ${purchase_price:.2f}\n"
                f"   Цена на маркете: ${market_price:.2f}\n"
                f"   Цена после комиссий: ${final_price:.2f}\n"
                f"   {'📈 Выгода' if profit_percent > 0 else '📉 Убыток'}: {profit_percent:.2f}%\n"
            )
        await message.answer("\n".join(response_lines))


# Новый обработчик для получения даты от пользователя
@router.message(FilterByDate.waiting_for_manual_date)
async def process_manual_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    try:
        datetime.strptime(date_text, "%Y-%m-%d")  # проверка формата даты
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
        return

    # Отправка чанками по 5
    CHUNK_SIZE = 5
    for i in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[i:i + CHUNK_SIZE]
        response_lines = [f"Скины за {date_text}:\n"]
        for idx, row in enumerate(chunk, start=i + 1):
            name, purchase_price, market_price, final_price, profit_percent, purchase_date = row
            response_lines.append(
                f"{idx}. {name}\n"
                f"   Дата покупки: {purchase_date}\n"
                f"   Цена покупки: ${purchase_price:.2f}\n"
                f"   Цена на маркете: ${market_price:.2f}\n"
                f"   Цена после комиссий: ${final_price:.2f}\n"
                f"   {'📈 Выгода' if profit_percent > 0 else '📉 Убыток'}: {profit_percent:.2f}%\n"
            )
    await message.answer("\n".join(response_lines), reply_markup=main_menu)
    await state.clear()  # очищаем состояние после обработки
