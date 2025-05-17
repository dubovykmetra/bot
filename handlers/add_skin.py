from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.add_skin import AddSkin
from services.exchange import get_usd_exchange_rate
from services.skins_api import CSPriceChecker
from db.database import add_skin_to_db
from datetime import datetime
from keyboards.reply import date_choice_keyboard
#from aiogram.types import ReplyKeyboardRemove

checker = CSPriceChecker()
checker.load_skin_names() 

router = Router()

@router.message(lambda message: message.text == "➕ Добавить скин" or message.text == "/add")
async def start_add_skin(message: types.Message, state: FSMContext):
    await state.clear()  # ← ОЧИСТКА ПРЕДЫДУЩИХ СОСТОЯНИЙ
    # current_state = await state.get_state()
    # await message.answer(f"Состояние после очистки: {current_state}")
    await message.answer("Введите название скина:")
    await state.set_state(AddSkin.waiting_for_name)

@router.message(AddSkin.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    # current_state = await state.get_state()
    # await message.answer(f"Состояние после очистки: {current_state}")
    await state.update_data(name=message.text)
    await message.answer("Введите цену покупки (в $ или грн):")
    await state.set_state(AddSkin.waiting_for_price)

@router.message(AddSkin.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    # current_state = await state.get_state()
    # await message.answer(f"Состояние после очистки: {current_state}")
    user_data = await state.get_data()
    name = user_data["name"]
    rate = get_usd_exchange_rate()
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с ценой.")
        return
    text = message.text.replace(",", ".")

    try:
        if text.startswith("$"):
            purchase_price = float(text[1:])
        else:
            purchase_price = float(text) / rate
    except:
        await message.answer("❌ Неверный формат цены. Повторите ввод.")
        return
    
    print(f"Вызов функции {checker.find_price(name)}")

    market_price = checker.find_price(name)
    if market_price is None:
        await message.answer(
            f"❌ Скин с именем «{name}» не найден. Попробуйте снова.\nВведите название скина:"
        )
        await state.clear()
        await state.set_state(AddSkin.waiting_for_name)
        return

    final_price = market_price * 0.95 * 0.95
    profit = (final_price - purchase_price * 1.042) / purchase_price * 100
    purchase_price *= 1.042

    # Сохраняем промежуточные данные и просим дату
    await state.update_data(
        purchase_price=purchase_price,
        market_price=market_price,
        final_price=final_price,
        profit=profit,
    )
    await message.answer(
        "Вы хотите использовать сегодняшнюю дату или ввести свою?",
        reply_markup=date_choice_keyboard
    )
    await state.set_state(AddSkin.waiting_for_date_choice)

@router.message(AddSkin.waiting_for_date_choice)
async def process_date_choice(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Состояние после очистки: {current_state}")
    if message.text == "📅 Сегодня":
        purchase_date = datetime.now().strftime("%Y-%m-%d")
        await finalize_skin_add(message, state, purchase_date)
    elif message.text == "✍️ Ввести вручную":
        await message.answer("Введите дату в формате ГГГГ-ММ-ДД:")
        await state.set_state(AddSkin.waiting_for_date)
    else:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")




@router.message(AddSkin.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    date_text = message.text.strip()

    if date_text == "":
        purchase_date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            dt = datetime.strptime(date_text, "%Y-%m-%d")
            purchase_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Введите дату в формате ГГГГ-ММ-ДД или оставьте пустым."
            )
            return

async def finalize_skin_add(message: types.Message, state: FSMContext, purchase_date: str):
    user_data = await state.get_data()
    name = user_data["name"]
    purchase_price = user_data["purchase_price"]
    market_price = checker.find_price(name)

    final_price = market_price * 0.95 * 0.95
    profit = (final_price - purchase_price) / purchase_price * 100

    add_skin_to_db(name, purchase_price, market_price, final_price, profit, purchase_date)

    await message.answer(
        f"✅ Скин: {name}\n"
        f"Дата покупки: {purchase_date}\n"
        f"Цена покупки: ${purchase_price:.2f}\n"
        f"Цена на маркете: ${market_price:.2f}\n"
        f"Цена после комиссий: ${final_price:.2f}\n"
        f"{'📈 Выгода' if profit > 0 else '📉 Убыток'}: {profit:.2f}%"
    )
    await state.clear()
    
    # Устанавливаем начальное состояние добавления скина
    await state.set_state(AddSkin.waiting_for_name)
    
    # Заново запускаем цикл
    await message.answer("Введите название следующего скина:")
