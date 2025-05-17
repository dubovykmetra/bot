from aiogram.fsm.state import StatesGroup, State

class AddSkin(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_date_choice = State()  # ← добавь это
    waiting_for_date = State()         # ← и это
