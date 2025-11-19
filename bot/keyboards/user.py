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

from aiogram.utils.keyboard import InlineKeyboardBuilder

def channels_keyboard(channels):
    builder = InlineKeyboardBuilder()

    for channel in channels:
        builder.button(
            text=channel.title,
            url=channel.link
        )

    builder.adjust(1)
    return builder.as_markup()