from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Contact Admin",
                    url="https://t.me/y_ahmedov"
                )
            ]
        ]
    )
    return keyboard

