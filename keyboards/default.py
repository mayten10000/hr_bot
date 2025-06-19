from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/candidates")]
        ],
        resize_keyboard=True
    )
