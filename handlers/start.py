from aiogram import Router, types
from aiogram.filters import Command
from keyboards.reply import main_menu
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # ← ОЧИСТКА ПРЕДЫДУЩИХ СОСТОЯНИЙ
    current_state = await state.get_state()
    await message.answer(f"Состояние после очистки: {current_state}")
    await message.answer(
        "Привет! Выбери действие:",
        reply_markup=main_menu
    )
