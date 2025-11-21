from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Send Message")],
            [KeyboardButton(text="📊 Stats")]
        ],
        resize_keyboard=True
    )
    return keyboard
