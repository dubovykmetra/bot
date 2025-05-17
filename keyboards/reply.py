from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить скин")],
        [KeyboardButton(text="Показать скины по дате")],
    ],
    resize_keyboard=True
)

date_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Сегодня")],
        [KeyboardButton(text="✍️ Ввести вручную")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

skin_list = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Сегодня")],
        [KeyboardButton(text="✍️ Ввести вручную")],
        [KeyboardButton(text="За все дни")],

    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)