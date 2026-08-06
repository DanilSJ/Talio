from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def payment_keyboard(url: str):
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Купить",
                    url=url,
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Проверить",
                    callback_data=f"payment_check",
                ),
            ],
        ]
    )

    return builder
