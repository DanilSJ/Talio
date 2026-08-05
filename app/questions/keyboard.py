from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def questions_menu():
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✔️Что из себя представляет ваш бот?",
                    callback_data="question_1",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Сообщения конфиденциальны?",
                    callback_data="question_2",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Это замена специалисту(коучу, наставнику, консультанту)?",
                    callback_data="question_3",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Есть ли лимиты на количество сообщений?",
                    callback_data="question_4",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Что даёт Premium-подписка?",
                    callback_data="question_5",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Как узнать, до какого числа активна Premium-подписка?",
                    callback_data="question_6",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✔️Как связаться с поддержкой?",
                    callback_data="question_7",
                ),
            ],
        ]
    )

    return builder


def questions_back():
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="question_back",
                ),
            ],
        ]
    )

    return builder
