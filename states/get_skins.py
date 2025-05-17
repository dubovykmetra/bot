from aiogram.fsm.state import StatesGroup, State

class FilterByDate(StatesGroup):
    waiting_for_date = State()
