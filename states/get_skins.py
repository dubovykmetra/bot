from aiogram.fsm.state import StatesGroup, State

class FilterByDate(StatesGroup):
    waiting_for_datess = State()
    waiting_for_manual_date = State()
