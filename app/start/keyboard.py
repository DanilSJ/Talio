from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="👤 Личный кабинет"),
        types.KeyboardButton(text="💎 Premium подписка"),
    )
    builder.row(
        types.KeyboardButton(text="❓ Вопрос-ответ"),
        types.KeyboardButton(text="👥 Пригласить друзей"),
    )
    builder.row(
        types.KeyboardButton(text="ℹ️ Условия использования"),
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
