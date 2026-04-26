from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

#Кнопки
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пройти опрос")],
        [KeyboardButton(text="Создать опрос")]
    ],
    resize_keyboard=True
)