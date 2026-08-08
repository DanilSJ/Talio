from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard():
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить промпт",
                    callback_data="admin_set_system_prompt",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Рассылка",
                    callback_data="admin_ads",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Статистика сообщений",
                    callback_data="admin_messages",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Включить/отключить QWEN",
                    callback_data="on_off_qwen",
                ),
            ],
        ]
    )

    return builder
